from collections import deque

from fft import find_two_independent_peaks, box_filter_reconstruct, get_magnitude_at_freq

from varie import open_serial, setup_exit, save_csv

from plotting import setup_live_plot, update_live_plot, setup_reconstruct_plot, update_reconstruct_plot

PORT = "COM3"
BAUD = 115200
BUFFER_SIZE = 1500
TIMEOUT = 1

DELTA = 2.0

FS_FIXED = 2445.0


def main():
    ser = open_serial(PORT, BAUD, TIMEOUT)

    print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")

    setup_exit()

    fig, ax = setup_live_plot()

    fig_rec, ax_rec, line_sig_1, line_sig_2 = setup_reconstruct_plot()

    lines = {}

    buffers = {}
    buffers["SIG"] = deque(maxlen=BUFFER_SIZE)

    sample_counter = 0
    last_fft_sample = 0

    serial_buffer = ""

    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")

    try:
        while True:

            raw = ser.read(ser.in_waiting or 1).decode(errors="ignore")
            serial_buffer += raw

            lines_raw = serial_buffer.split("\n")
            serial_buffer = lines_raw[-1]

            for line in lines_raw[:-1]:

                parts = line.strip().split()

                if len(parts) != 1:
                    continue

                try:
                    v = int(parts[0])
                except:
                    continue

                buffers["SIG"].append(v)

                sample_counter += 1

            if (
                len(buffers["SIG"]) == BUFFER_SIZE
                and sample_counter - last_fft_sample >= BUFFER_SIZE
            ):

                last_fft_sample = sample_counter

                sample_rate = FS_FIXED

                sig = list(buffers["SIG"])

                f1, f2, debug_info = find_two_independent_peaks(
                    sig,
                    sample_rate,
                    f_min=10.0,
                    f_max=120.0,
                    delta_hz=DELTA,
                    min_sep_hz=5.0,
                    min_score_ratio=0.20,
                    return_debug=True
                )

                if f1 is None or f2 is None:
                    print("[WARN] Non sono state trovate due componenti affidabili.\n")
                    continue

                print("\n[DEBUG] Picchi indipendenti trovati:")

                for item in debug_info:
                    print(
                        f"picco={item['peak']:.2f} Hz | "
                        f"score={item['score']:.2f}"
                    )

                if f1 > f2:
                    f1, f2 = f2, f1

                mag1 = get_magnitude_at_freq(sig, sample_rate, f1, delta_hz=DELTA)
                mag2 = get_magnitude_at_freq(sig, sample_rate, f2, delta_hz=DELTA)

                print(
                    f"\n[SIG] fs={sample_rate:.2f} Hz "
                    f"→ fondamentali stimate: {f1:.2f} Hz, {f2:.2f} Hz"
                )

                print("Magnitude potenziometro 1:", round(mag1, 2))
                print("Magnitude potenziometro 2:", round(mag2, 2))

                y1 = box_filter_reconstruct(
                    sig,
                    sample_rate,
                    f0=f1,
                    delta_hz=DELTA
                )

                y2 = box_filter_reconstruct(
                    sig,
                    sample_rate,
                    f0=f2,
                    delta_hz=DELTA
                )

                update_reconstruct_plot(
                    ax_rec,
                    line_sig_1,
                    line_sig_2,
                    y1,
                    y2,
                    f1,
                    f2
                )

                save_csv("SIG_box.csv", sig, y1, f1)

            update_live_plot(ax, buffers, lines, BUFFER_SIZE)

    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()


if __name__ == "__main__":
    main()