import difflib
import os
import re
from pathlib import Path
from typing import List

import assemblyai as aai
import requests
from assemblyai import WordBoost
from pydantic import BaseModel


class Word(BaseModel):
    text: str
    time_start: float  # seconds
    time_end: float  # seconds


class Transcript(BaseModel):
    words: List[Word]


def transcribe_lyrics(vocals_file: Path, artist: str, title: str) -> Transcript:
    out_path = Path(f"cache/lyrics/{vocals_file.stem}.json")
    if out_path.is_file():
        print("Lyrics transcription is already cached")
        transcript = Transcript.parse_file(out_path)
    else:
        transcript = None

    known_words = get_known_words(artist, title)

    if transcript is None:
        print("Transcribing lyrics...")
        api_key = os.environ.get("ASSEMBLY_AI_API_KEY")
        if not api_key:
            print("WARNING: ASSEMBLY_AI_API_KEY isn't set. Skipping transcription.")
            return Transcript(words=[])

        aai.settings.api_key = api_key
        config = aai.TranscriptionConfig(
            punctuate=False,  # Remove punctuation
            format_text=False,  # Don't convert numbers to text
            # disfluencies=True,  # Keep "filler" words
            word_boost=list(
                set(known_words)
            ),  # Increase the weight of words we expect to be included
            boost_param=WordBoost.high,  # By a lot
        )
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(str(vocals_file), config)

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(transcript.error)
        print("transcription done")

        words = []
        for word in transcript.json_response["words"]:
            words.append(
                Word(
                    text=word["text"],
                    time_start=word["start"] / 1_000,
                    time_end=word["end"] / 1_000,
                )
            )
        transcript = Transcript(words=words)
        out_path.parent.mkdir(exist_ok=True, parents=True)
        out_path.write_text(transcript.json())

    transcript = fix_transcript(transcript, known_words)
    return transcript


def fix_transcript(transcript: Transcript, known_words: list[str]) -> Transcript:
    s = difflib.SequenceMatcher(a=[x.text for x in transcript.words], b=known_words)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            continue
        if i2 - i1 > 10 or j2 - j1 > 10:
            # Skips long diffs (likely to move chorus around or similar)
            continue
        if tag == "replace":
            if i2 - i1 == j2 - j1:
                # Identical shapes, we can just replace the texts
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    print(f"replacing '{transcript.words[i]}' by '{known_words[j]}'")
                    transcript.words[i].text = known_words[j]
        else:
            # TODO: maybe figure out how to handle other kinds of diffs
            pass
    return transcript


# Pre-filter words for a better transcription by checking lyrics dbs
# (we still need the actual transcription for timing data)
def get_known_words(artist, title) -> List[str]:
    try:
        out_path = Path(
            f"cache/lyrics/{artist.replace(' ', '_')}--{title.replace(' ', '_')}.raw.txt"
        )
        if out_path.is_file():
            print("raw lyrics are already cached")
            raw_lyrics = out_path.read_text()
        else:
            r = requests.get(f"https://api.lyrics.ovh/v1/{artist}/{title}", timeout=10)
            r.raise_for_status()
            raw_lyrics = r.json()["lyrics"]
            out_path.parent.mkdir(exist_ok=True, parents=True)
            out_path.write_text(raw_lyrics)
        print(f"Full lyrics: {raw_lyrics}")
        res = raw_lyrics_to_words(raw_lyrics)
        print(f"Got lyrics word set for transcription weighting: {set(res)}")
        return res
    except Exception as e:
        print(f"Can't access lyrics database, skipping word weighing: {e}")
        return []


def raw_lyrics_to_words(raw: str) -> List[str]:
    pattern = re.compile("[^a-zA-Z']")
    res = list()
    for word in raw.split():
        word = pattern.sub("", word.lower())
        if word:
            res.append(word)
    return res
