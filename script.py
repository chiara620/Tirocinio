import time
from collections import deque
from fft import do_fft, signal_reconstruction, find_two_dominant_freqs, box_filter_reconstruct
from varie import open_serial, setup_exit, save_csv
from plotting import setup_live_plot, update_live_plot, setup_reconstruct_plot, update_reconstruct_plot

PORT = "COM3"
BAUD = 115200
BUFFER_SIZE = 500
TIMEOUT = 1

FFT_EVERY = 10  # fft ogni 10 buffer pieni

DELTA = 5.0  # larghezza box passabanda in Hz

def main():
    ser = open_serial(PORT, BAUD, TIMEOUT)
    print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")
    setup_exit()
    fig, ax = setup_live_plot()
    fig_rec, ax_rec, line_sig_1, line_sig_2 = setup_reconstruct_plot()

    lines = {}
    buffers = {}
    buffers["SIG"] = deque(maxlen=BUFFER_SIZE)

    timestamps = deque(maxlen=BUFFER_SIZE)
    prev_ts = None

    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")

    try:
        while True:
            raw = ser.read(ser.in_waiting or 1).decode(errors="ignore")

            for line in raw.splitlines():
                parts = line.strip().split()
                if len(parts) != 1:
                    continue

                try:
                    v = int(parts[0])
                except:
                    continue

                buffers["SIG"].append(v)

                now = time.time()   # calcolo timestamp per fs
                if prev_ts is not None:
                    timestamps.append(now - prev_ts)
                prev_ts = now

            if len(buffers["SIG"]) == BUFFER_SIZE:   # fft quando buffer pieno
                sample_rate = 1 / (sum(timestamps) / len(timestamps))
                if not (1000 < sample_rate < 3000): # salto il junk
                    continue

                f1, f2 = find_two_dominant_freqs(
                    list(buffers["SIG"]),
                    sample_rate,
                    f_min=1.0,
                    f_max=200.0,
                    min_sep_hz=5.0
                )

                if f1 is None or f2 is None:
                    continue

                print(f"[SIG] fs={sample_rate:.2f} → picchi: {f1:.2f} Hz, {f2:.2f} Hz")

                y1 = box_filter_reconstruct(list(buffers["SIG"]), sample_rate, f0=f1, delta_hz=DELTA)
                y2 = box_filter_reconstruct(list(buffers["SIG"]), sample_rate, f0=f2, delta_hz=DELTA)

                update_reconstruct_plot(ax_rec, line_sig_1, line_sig_2, y1, y2, f1, f2)

                save_csv("SIG_box.csv", list(buffers["SIG"]), y1, f1)

            update_live_plot(ax, buffers, lines, BUFFER_SIZE)

    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()

if __name__ == "__main__":
    main()
