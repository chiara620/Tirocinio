import matplotlib.pyplot as plt
import numpy as np

def setup_live_plot():
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_ylim(0, 1023)
    ax.set_xlabel("Campioni (ultimi N)")
    ax.set_ylabel("Valore analogico")
    ax.set_title("Lettura in tempo reale")
    return fig, ax


def update_live_plot(ax, buffers, lines, buffer_size):
    for pin, buf in buffers.items():
        if pin not in lines:
            (lines[pin],) = ax.plot([], [], label=pin)
            ax.legend()

        xdata = range(len(buf))
        ydata = list(buf)
        lines[pin].set_data(xdata, ydata)

    if len(buffers) > 0:
        max_len = max(len(buf) for buf in buffers.values())
        ax.set_xlim(max(0, max_len - buffer_size), max_len)

    plt.pause(0.01)


def setup_fft_plot():
    plt.ion()
    fig_fft, ax_fft = plt.subplots()
    (line_fft,) = ax_fft.plot([], [], lw=1)
    ax_fft.set_xlabel("Frequenza [Hz]")
    ax_fft.set_ylabel("Ampiezza")
    ax_fft.set_title("FFT in tempo reale")
    ax_fft.grid(True)
    return fig_fft, ax_fft, line_fft


def update_fft_plot(ax_fft, line_fft, xf, amplitudes):
    line_fft.set_data(xf, amplitudes)
    ax_fft.relim()
    ax_fft.autoscale_view()
    plt.pause(0.05)


def setup_reconstruct_plot():
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_title("Ricostruzione tramite troncamento Fourier")
    ax.set_xlabel("Campioni")
    ax.set_ylabel("Valore ricostruito")
    ax.grid(True)

    line_A0, = ax.plot([], [], label="Ricostruzione A0", linestyle='--')
    line_A2, = ax.plot([], [], label="Ricostruzione A2", linestyle='-.')

    ax.legend()
    return fig, ax, line_A0, line_A2


def update_reconstruct_plot(ax, line_A0, line_A2, recon_A0, recon_A2):
    x = np.arange(len(recon_A0))

    line_A0.set_data(x, recon_A0)
    line_A2.set_data(x, recon_A2)

    ax.set_xlim(0, len(recon_A0))

    all_vals = np.concatenate([recon_A0, recon_A2])
    ax.set_ylim(np.min(all_vals) * 0.9, np.max(all_vals) * 1.1)

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

