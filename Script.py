import time
from collections import deque
from fft import do_fft
from plotting import setup_live_plot, update_live_plot, setup_fft_plot, update_fft_plot
from varie import open_serial, parse_line, setup_safe_exit

PORT = "COM3"
BAUD = 115200
BUFFER_SIZE = 100
TIMEOUT = 1

def main():
    ser = open_serial(PORT, BAUD, TIMEOUT)
    print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")
    setup_safe_exit()

    fig, ax = setup_live_plot()
    buffers = {}
    lines = {}

    fig_fft, ax_fft, line_fft = setup_fft_plot()    # crea finestra fft una sola volta

    timestamps = deque(maxlen=BUFFER_SIZE)
    prev_ts = None

    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")

    try:
        while True:
            serial_line = ser.readline()
            now = time.time()
            if prev_ts is not None:
                timestamps.append(now - prev_ts)
            prev_ts = now

            v = parse_line(serial_line)
            if v is None:
                continue

            ts = time.time()
            for pin, value in v.items():
                if pin not in buffers:
                    buffers[pin] = deque(maxlen=BUFFER_SIZE)
                buffers[pin].append(value)

                if len(buffers[pin]) == BUFFER_SIZE and len(timestamps) > 10:   # fft quando buffer pieno
                    sample_rate = 1 / (sum(timestamps) / len(timestamps))
                    xf, amp, dom = do_fft(buffers[pin], sample_rate)
                    print(f"[FFT] {pin}: fs={sample_rate:.2f} Hz → freq dominante ≈ {dom:.2f} Hz")

                    update_fft_plot(ax_fft, line_fft, xf, amp)

            update_live_plot(ax, buffers, lines, BUFFER_SIZE)

    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()

if __name__ == "__main__":
    main()
