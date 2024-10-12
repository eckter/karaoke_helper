import os
from pathlib import Path
from typing import List

import assemblyai as aai
from pydantic import BaseModel


class Word(BaseModel):
    text: str
    time_start: float  # seconds
    time_end: float  # seconds


class Transcript(BaseModel):
    words: List[Word]


def transcribe_lyrics(vocals_file: Path) -> Transcript:
    out_path = Path(f"cache/lyrics/{vocals_file.stem}.json")
    if out_path.is_file():
        print("Lyrics transcription is already cached")
        return Transcript.parse_file(out_path)
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

    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(transcript.json())
    return transcript
