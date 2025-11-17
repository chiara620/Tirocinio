import serial
import time
import signal
import sys
import warnings
import matplotlib
matplotlib.use("TkAgg")
import csv

def save_csv(filename, original, reconstructed, freq):
    N = len(original)
    if len(reconstructed) != N:
        raise ValueError("Original and reconstructed must have same length")

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "original", "reconstructed", "freq"])

        for i in range(N):
            writer.writerow([i, original[i], reconstructed[i], freq])


def open_serial(port, baud, timeout=0.1):
    ser = serial.Serial(port, baud, timeout=timeout)
    time.sleep(2)
    ser.reset_input_buffer()
    return ser


def setup_exit():
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")    # ignoro junk warning

    def handler(sig, frame):
        print("\n[STOP] Interruzione da tastiera. Chiusura.")
        try:
            import matplotlib.pyplot as plt
            plt.close('all')  # chiude tutte le finestre grafiche
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)