import numpy as np

# Typing aliases used to type ndarray dimensions
NFrequencies = int
NSamples = int
NNotes = int

Spectrogram = np.ndarray[NFrequencies, NSamples]
Pitches = np.ndarray[NSamples, NNotes]
