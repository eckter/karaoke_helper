import sys

from karaoke_helper.audio_processing.lyrics_transcription import transcribe_lyrics
from karaoke_helper.runner import Runner
from karaoke_helper.ui.playback import Playback, Playbacks
from karaoke_helper.ui.ui import UI

from .audio_processing.pitch_tracker import audio_to_pitches
from .audio_processing.song_loading import load_file_raw, load_yt_url, split_vocals


def entrypoint():
    artist, title = sys.argv[1], sys.argv[2]
    raw = load_yt_url(artist, title)
    vocals, instru = split_vocals(raw)
    vocals_audio, vocals_sr = load_file_raw(vocals)
    instru_audio, instru_sr = load_file_raw(instru)

    pitches = audio_to_pitches(vocals_audio)
    transcription = transcribe_lyrics(vocals, artist, title)

    playbacks = Playbacks(
        [
            Playback(vocals_audio, vocals_sr),
            Playback(instru_audio, instru_sr),
        ]
    )
    playbacks.start()
    runner = Runner(pitches, transcription, UI(transcription))
    runner.run()


if __name__ == "__main__":
    entrypoint()
