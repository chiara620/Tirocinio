import numpy as np
from numpy.fft import fft, ifft, fftfreq, rfft, rfftfreq

def positive_spectrum(buffer, fs):
    x = np.asarray(buffer, dtype=float)

    if len(x) == 0:
        return None, None

    x = x - np.mean(x)

    N = len(x)
    freqs = rfftfreq(N, d=1 / fs)
    X = rfft(x)

    # Ampiezza normalizzata monolato
    amp = 2 * np.abs(X) / N

    # Ignora componente DC
    if len(amp) > 0:
        amp[0] = 0

    return freqs, amp


def band_magnitude(freqs, amp, center_freq, delta_hz):
    mask = np.abs(freqs - center_freq) <= delta_hz

    if not np.any(mask):
        return 0.0

    return np.sqrt(np.sum(amp[mask] ** 2))


def get_magnitude_at_freq(buffer, fs, target_freq, delta_hz=3.0):
    freqs, amp = positive_spectrum(buffer, fs)

    if freqs is None:
        return 0.0

    return band_magnitude(freqs, amp, target_freq, delta_hz)


def find_local_peaks(freqs, amp, f_min, f_max, max_peaks=20):
    if freqs is None or amp is None or len(freqs) < 3:
        return []

    peak_indices = []

    for i in range(1, len(amp) - 1):
        if freqs[i] < f_min or freqs[i] > f_max:
            continue

        if amp[i] > amp[i - 1] and amp[i] >= amp[i + 1]:
            peak_indices.append(i)

    peak_indices = sorted(peak_indices, key=lambda i: amp[i], reverse=True)

    return peak_indices[:max_peaks]


def is_harmonic_related(fa, fb, tolerance_hz=2.0, max_ratio=9):
    if fa <= 0 or fb <= 0:
        return False

    small = min(fa, fb)
    large = max(fa, fb)

    for k in range(2, max_ratio + 1):
        if abs(large - k * small) <= tolerance_hz:
            return True

    return False


def score_square_family(freqs, amp, f0, delta_hz=3.0, spectrum_max=120.0):
    harmonics = [1, 3, 5, 7]
    weights = {
        1: 1.00,
        3: 0.60,
        5: 0.35,
        7: 0.20,
    }

    score = 0.0
    components = []

    for h in harmonics:
        fh = h * f0

        if fh > spectrum_max:
            continue

        mag = band_magnitude(freqs, amp, fh, delta_hz)
        weighted = weights[h] * mag
        score += weighted

        components.append({
            "harmonic": h,
            "freq": fh,
            "mag": mag,
            "weighted": weighted
        })

    fundamental_mag = band_magnitude(freqs, amp, f0, delta_hz)

    return score, fundamental_mag, components


def cluster_candidates(candidates, tolerance_hz):
    if not candidates:
        return []

    candidates = sorted(candidates)
    clusters = []

    current = [candidates[0]]

    for c in candidates[1:]:
        if abs(c - np.mean(current)) <= tolerance_hz:
            current.append(c)
        else:
            clusters.append(np.mean(current))
            current = [c]

    clusters.append(np.mean(current))

    return clusters


def find_two_independent_peaks(
    buffer,
    fs,
    f_min=10.0,
    f_max=120.0,
    delta_hz=2.0,
    min_sep_hz=5.0,
    min_score_ratio=0.20,
    return_debug=False
):
    freqs, amp = positive_spectrum(buffer, fs)

    if freqs is None:
        return (None, None, []) if return_debug else (None, None)

    work_amp = amp.copy()
    selected = []
    debug = []

    for _ in range(2):
        mask = (freqs >= f_min) & (freqs <= f_max)

        if not np.any(mask):
            break

        idx_candidates = np.where(mask)[0]
        idx_peak = idx_candidates[np.argmax(work_amp[idx_candidates])]

        f_peak = freqs[idx_peak]
        peak_amp = work_amp[idx_peak]

        if peak_amp <= 0:
            break

        if selected:
            first_score = debug[0]["score"]
            if peak_amp < first_score * min_score_ratio:
                break

        selected.append(f_peak)

        debug.append({
            "peak": f_peak,
            "score": peak_amp
        })

        # Sopprimi il picco scelto e le sue armoniche
        for h in [1, 2, 3, 4, 5, 6, 7]:
            fh = f_peak * h
            if fh > f_max:
                continue

            suppress_mask = np.abs(freqs - fh) <= delta_hz
            work_amp[suppress_mask] = 0

        # Sopprimi anche eventuali subarmoniche evidenti (es se scelgo 40hz non voglio prendere 20)
        for h in [2, 3, 4, 5, 6, 7]:
            fh = f_peak / h
            if fh < f_min:
                continue

            suppress_mask = np.abs(freqs - fh) <= delta_hz
            work_amp[suppress_mask] = 0

    if len(selected) < 2:
        return (None, None, debug) if return_debug else (None, None)

    f1, f2 = selected[0], selected[1]

    if abs(f1 - f2) < min_sep_hz:
        return (None, None, debug) if return_debug else (None, None)

    if f1 > f2:
        f1, f2 = f2, f1

    return (f1, f2, debug) if return_debug else (f1, f2)


def box_filter_reconstruct(buffer, fs, f0, delta_hz):
    x = np.asarray(buffer, dtype=float)
    x = x - np.mean(x)

    N = len(x)
    X = fft(x)
    f = fftfreq(N, 1 / fs)

    mask = (np.abs(f - f0) <= delta_hz) | (np.abs(f + f0) <= delta_hz)

    Xf = np.zeros_like(X)
    Xf[mask] = X[mask]

    y_rec = np.real(ifft(Xf))
    return y_rec


def signal_reconstruction(x, fs, N_harmonics=10):
    N = len(x)
    X = fft(x)

    X_filtered = np.zeros_like(X)
    X_filtered[:N_harmonics + 1] = X[:N_harmonics + 1]
    X_filtered[-N_harmonics:] = X[-N_harmonics:]

    recon = np.real(ifft(X_filtered))
    return recon