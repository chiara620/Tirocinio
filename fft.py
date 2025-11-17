import numpy as np
from scipy.fft import fft,  ifft, fftfreq

# 38, 17

def do_fft(buffer, fs):
    N = len(buffer)
    if N == 0:
        return None, None, None

    y = np.array(buffer, dtype=float)
    y = y - np.mean(y)  # rimuovi DC

    yf = fft(y)
    xf = fftfreq(N, 1/fs)

    amp = np.abs(yf)

    dominant_idx = np.argmax(amp[1:]) + 1       # ignora il bin 0 (DC)
    dominant_freq = xf[dominant_idx]

    return xf, amp, dominant_freq


def signal_reconstruction(x, fs, N_harmonics=10):
    N = len(x)
    X = fft(x)

    X_filtered = np.zeros_like(X)   # mantieni solo le prime N_harmonics frequenze positive
    X_filtered[:N_harmonics+1] = X[:N_harmonics+1]
    X_filtered[-N_harmonics:] = X[-N_harmonics:]

    recon = np.real(ifft(X_filtered))
    return recon
