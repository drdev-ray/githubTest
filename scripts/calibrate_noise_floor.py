"""Optional helper to measure ambient noise level."""
# TODO: add unit tests

import soundfile as sf
import sounddevice as sd
import numpy as np

print("Recording 15 seconds of ambient noise...")
rec = sd.rec(int(15 * 16000), samplerate=16000, channels=1)
sd.wait()
level = 20 * np.log10((rec**2).mean() ** 0.5)
print(f"Suggested threshold: {level + 12:.1f} dB")
