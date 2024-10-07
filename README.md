This is an early prototype for a tool that helps with singing.
The goal is to imitate karaoke software with pitch visualization, but without any catalogue restriction.
It's not functional yet, just an incremental POC.

The main pipeline is:
1. youtube url
2. -> audio download
3. -> vocals/instrumental split
4. -> pitch tracking
5. -> comparaison with mic pitch tracking

Eventually, I could add playback, lyrics transcription, and other cool stuff.

### Requirements

1. Poetry
2. [spleeter](https://github.com/deezer/spleeter), to be cloned at the root of the repo (or clone this with `--recursive`). I wish I could just handle it as a normal library, but versions are incompatible, and it can only be used with its CLI
4. There may be extra requirement to make mic work, depending on the OS. I wans't extra careful about what I needed to make it run, google any error message and contact me to add stuff to this list

### Usage

`poetry run karaoke_helper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`
