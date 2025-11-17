import time
from collections import deque
from fft import do_fft, signal_reconstruction
from varie import open_serial, setup_exit, save_csv
from plotting import setup_live_plot, update_live_plot, setup_reconstruct_plot, update_reconstruct_plot

PORT = "COM3"
BAUD = 115200
BUFFER_SIZE = 500
TIMEOUT = 1

FFT_EVERY = 10  # calcola FFT ogni 10 buffer pieni

def main():
    ser = open_serial(PORT, BAUD, TIMEOUT)
    print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")
    setup_exit()
    fig, ax = setup_live_plot()
    fig_rec, ax_rec, line_A0, line_A2 = setup_reconstruct_plot()

    lines = {}
    buffers = {}
    buffers["A0"] = deque(maxlen=BUFFER_SIZE)
    buffers["A2"] = deque(maxlen=BUFFER_SIZE)

    timestamps = deque(maxlen=BUFFER_SIZE)
    prev_ts = None

    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")


    try:
        while True:
            raw = ser.read(ser.in_waiting or 1).decode(errors="ignore")

            for line in raw.splitlines():
                parts = line.strip().split()
                if len(parts) != 2:
                    continue

                try:
                    a0 = int(parts[0])
                    a2 = int(parts[1])
                except:
                    continue

                buffers["A0"].append(a0)
                buffers["A2"].append(a2)

                now = time.time()   # calcolo timestamp per fs
                if prev_ts is not None:
                    timestamps.append(now - prev_ts)
                prev_ts = now

            if len(buffers["A0"]) == BUFFER_SIZE:   # fft quando buffer pieno
                sample_rate = 1 / (sum(timestamps) / len(timestamps))
                if not (1000 < sample_rate < 3000): # salto il junk
                    continue    
                xf0, amp0, dom0 = do_fft(buffers["A0"], sample_rate)
                xf2, amp2, dom2 = do_fft(buffers["A2"], sample_rate)

                print(f"[A0] fs={sample_rate:.2f} → f={dom0:.2f}")
                print(f"[A2] fs={sample_rate:.2f} → f={dom2:.2f}")

                # ricostruzione tramite Fourier troncato
                recon_A0 = signal_reconstruction(list(buffers["A0"]), sample_rate, N_harmonics=100)
                recon_A2 = signal_reconstruction(list(buffers["A2"]), sample_rate, N_harmonics=100)
                update_reconstruct_plot(ax_rec, line_A0, line_A2, recon_A0, recon_A2)

                save_csv("A0_output.csv", list(buffers["A0"]), recon_A0, dom0)
                save_csv("A2_output.csv", list(buffers["A2"]), recon_A2, dom2)

            update_live_plot(ax, buffers, lines, BUFFER_SIZE)


    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()


if __name__ == "__main__":
    main()
