This is an early prototype for a tool that helps with singing.
The goal is to imitate karaoke software with pitch visualization, but without any catalogue restriction.
It's not functional yet, just an incremental POC.

The main pipeline is:
1. youtube url
2. -> audio download
3. -> vocals/instrumental split
4. -> pitch tracking
5. -> comparaison with mic pitch tracking
6. If assembly ai api key is set, vocals are sent for lyrics transcription


### Requirements

1. Python, 3.10 specifically for spleeter.
1. Poetry
3. `ffmpeg` and `libportaudio2`. On Ubuntu-based distributions, `sudo apt install ffmpeg libportaudio2`.
4. (optional) For lyrics transcription, an AssemblyAI key should be set in env variable `ASSEMBLY_AI_API_KEY`. It costs roughly $0.01 credits per song.

Note: it shouldn't be linux specific, but installing requirements is less convenient on Windows. 

### Usage

`poetry run karaoke_helper "Rick Astley" "Never Gonna Give You Up"`
