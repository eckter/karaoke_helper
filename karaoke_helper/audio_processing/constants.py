from dataclasses import dataclass
from enum import Enum

import numpy as np
from sortedcontainers import SortedDict


class Note(Enum):
    C = 0
    CS = 1
    D = 2
    DS = 3
    E = 4
    F = 5
    FS = 6
    G = 7
    GS = 8
    A = 9
    AS = 10
    B = 11


@dataclass
class AbsoluteNote:
    note: Note
    octave: int


# https://en.wikipedia.org/wiki/Vocal_range#Operatic_six_basic_voice_types
# Highest note has been removed so that highest B can wrap back to lowest C
SINGABLE_NOTE_MAPPING = SortedDict(
    {
        65.40639: AbsoluteNote(Note.C, 2),
        69.29566: AbsoluteNote(Note.CS, 2),
        73.41619: AbsoluteNote(Note.D, 2),
        77.78175: AbsoluteNote(Note.DS, 2),
        82.40689: AbsoluteNote(Note.E, 2),
        87.30706: AbsoluteNote(Note.F, 2),
        92.49861: AbsoluteNote(Note.FS, 2),
        97.99886: AbsoluteNote(Note.G, 2),
        103.8262: AbsoluteNote(Note.GS, 2),
        110.0000: AbsoluteNote(Note.A, 2),
        116.5409: AbsoluteNote(Note.AS, 2),
        123.4708: AbsoluteNote(Note.B, 2),
        130.8128: AbsoluteNote(Note.C, 3),
        138.5913: AbsoluteNote(Note.CS, 3),
        146.8324: AbsoluteNote(Note.D, 3),
        155.5635: AbsoluteNote(Note.DS, 3),
        164.8138: AbsoluteNote(Note.E, 3),
        174.6141: AbsoluteNote(Note.F, 3),
        184.9972: AbsoluteNote(Note.FS, 3),
        195.9977: AbsoluteNote(Note.G, 3),
        207.6523: AbsoluteNote(Note.GS, 3),
        220.0000: AbsoluteNote(Note.A, 3),
        233.0819: AbsoluteNote(Note.AS, 3),
        246.9417: AbsoluteNote(Note.B, 3),
        261.625: AbsoluteNote(Note.C, 4),
        277.182: AbsoluteNote(Note.CS, 4),
        293.664: AbsoluteNote(Note.D, 4),
        311.127: AbsoluteNote(Note.DS, 4),
        329.6276: AbsoluteNote(Note.E, 4),
        349.2282: AbsoluteNote(Note.F, 4),
        369.9944: AbsoluteNote(Note.FS, 4),
        391.9954: AbsoluteNote(Note.G, 4),
        415.3047: AbsoluteNote(Note.GS, 4),
        440.0000: AbsoluteNote(Note.A, 4),
        466.1638: AbsoluteNote(Note.AS, 4),
        493.8833: AbsoluteNote(Note.B, 4),
        523.2511: AbsoluteNote(Note.C, 5),
        554.3653: AbsoluteNote(Note.CS, 5),
        587.3295: AbsoluteNote(Note.D, 5),
        622.2540: AbsoluteNote(Note.DS, 5),
        659.2551: AbsoluteNote(Note.E, 5),
        698.4565: AbsoluteNote(Note.F, 5),
        739.9888: AbsoluteNote(Note.FS, 5),
        783.9909: AbsoluteNote(Note.G, 5),
        830.6094: AbsoluteNote(Note.GS, 5),
        880.0000: AbsoluteNote(Note.A, 5),
        932.3275: AbsoluteNote(Note.AS, 5),
        987.7666: AbsoluteNote(Note.B, 5),
    }
)

SINGABLE_NOTE_FREQUENCIES = np.array(SINGABLE_NOTE_MAPPING.keys())

# Threshold where we go from one note to the next
# (average between any pair of frequencies)
# (not technically correct as it should be logarithmic but good enough)
SINGABLE_NOTE_BOUNDARIES = np.convolve(
    SINGABLE_NOTE_FREQUENCIES, np.ones(2) / 2, mode="valid"
)

# Upscale the frequencies used, just to make it easier
# to figure out when we're a little off
halfway_values = (SINGABLE_NOTE_FREQUENCIES[:-1] + SINGABLE_NOTE_FREQUENCIES[1:]) / 2
UPSCALE_SINGABLE_NOTE_FREQUENCIES = np.insert(
    SINGABLE_NOTE_FREQUENCIES, range(1, len(SINGABLE_NOTE_FREQUENCIES)), halfway_values
)
UPSCALE_SINGABLE_NOTE_BOUNDARIES = np.convolve(
    UPSCALE_SINGABLE_NOTE_FREQUENCIES, np.ones(2) / 2, mode="valid"
)
