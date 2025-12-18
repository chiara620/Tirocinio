import numpy as np
from scipy.fft import fft,  ifft, fftfreq

# 38, 18

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


def find_two_dominant_freqs(buffer, fs, f_min=1.0, f_max=200.0, min_sep_hz=5.0):
    N = len(buffer)
    if N == 0:
        return None, None

    y = np.array(buffer, dtype=float)
    y = y - np.mean(y)

    Y = fft(y)
    f = fftfreq(N, 1/fs)

    amp = np.abs(Y) # ampiezza dello spettro

    mask = (f > 0) & (f >= f_min) & (f <= f_max)    # considero solo le frequenze positive e dentro [f_min, f_max]
    f_pos = f[mask]
    amp_pos = amp[mask]

    if len(f_pos) == 0:
        return None, None

    idx_sorted = np.argsort(amp_pos)[::-1]  # ordino i picchi per ampiezza decrescente

    f1 = f_pos[idx_sorted[0]]
    f2 = None
    for idx in idx_sorted[1:]:
        candidate = f_pos[idx]
        if abs(candidate - f1) >= min_sep_hz:
            f2 = candidate
            break

    return f1, f2


def box_filter_reconstruct(buffer, fs, f0, delta_hz):
    x = np.asarray(buffer, dtype=float)
    x = x - np.mean(x)

    N = len(x)
    X = fft(x)
    f = fftfreq(N, 1/fs)

    mask = (np.abs(f - f0) <= delta_hz) | (np.abs(f + f0) <= delta_hz)

    Xf = np.zeros_like(X)
    Xf[mask] = X[mask]

    y_rec = np.real(ifft(Xf))
    return y_rec

