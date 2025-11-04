import numpy as np
from scipy.fft import fft, fftfreq

def do_fft(buffer, rate):
    N = len(buffer)
    if N == 0:
        return None, None, None

    y = np.array(buffer)
    y = y - np.mean(y)  #####

    yf = fft(y)
    xf = fftfreq(N, 1 / rate)
    amplitudes = np.abs(yf)

    dominant_idx = np.argmax(amplitudes)
    dominant_freq = xf[dominant_idx]

    return xf, amplitudes, dominant_freq