This is an early prototype for a tool that helps with singing.
The goal is to imitate karaoke software with pitch visualization, but without any catalogue restriction.

The main pipeline is:
1. Input as artist + song name
2. -> Youtube lookup
3. -> audio download
4. -> vocals/instrumental split
5. -> pitch tracking
6. -> comparaison with mic pitch tracking
7. If an assembly ai api key is set, vocals are sent for lyrics transcription

Note: lyric transcription through assembly.ai isn't free, but it costs roughly $0.01 per song, out of $50 free credits for new accounts. 


### Requirements

1. Python, 3.11 (specifically for spleeter).
1. Poetry
3. `ffmpeg` and `libportaudio2`. On Ubuntu-based distributions, `sudo apt install ffmpeg libportaudio2`.
4. (optional) For lyrics transcription, an AssemblyAI key should be set in env variable `ASSEMBLY_AI_API_KEY`. It costs roughly $0.01 credits per song.

Note: it shouldn't be linux specific, but installing requirements is less convenient on Windows. 
Especially as this depends on Spleeter, which pins its dependencies to versions that have no wheel for Windows.
Maybe I'll try to open a PR on Spleeter to update its dependencies.

### Usage

`poetry run karaoke_helper "The Beatles" "Blackbird"`

Which then looks like this:

<img width="1400" height="778" alt="image" src="https://github.com/user-attachments/assets/b73e2bc2-13b7-422d-98a2-9ceaefce526b" />

### How do I read this, how do I know I'm singing in tune?

The horizontal axis is the time (left to right), with the vertical red line being "now". 

The vertical axis is how "high" a pitch is, and the color shows the intensity of that pitch at any given time. But there's more than one line, because [harmonics](https://en.wikipedia.org/wiki/Harmonic) are also displayed.

To match exactly the original singer's pitch, your lowest line should line up with their lowest line. 
To sound "in tune", any of your line needs to line up with any of the singer's line. This may harmonize and add some colour to the song, but it never sounds out of tune. 

There's of course some noise, which should be ignored. Sometimes, electric guitar riffs aren't split properly from the vocals and their pitch can show up. 
