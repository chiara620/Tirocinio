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
    ax.set_title("Segnali separati (box filter in FFT)")
    ax.set_xlabel("Campioni")
    ax.set_ylabel("Valore ricostruito")
    ax.grid(True)

    line_sig_1, = ax.plot([], [], label="Componente 1", linestyle='--')
    line_sig_2, = ax.plot([], [], label="Componente 2", linestyle='-.')

    ax.legend()
    return fig, ax, line_sig_1, line_sig_2


def update_reconstruct_plot(ax, line_sig_1, line_sig_2, y1, y2, f1, f2):
    x = np.arange(len(y1))

    line_sig_1.set_data(x, y1)
    line_sig_2.set_data(x, y2)

    line_sig_1.set_label(f"Componente ~ {f1:.1f} Hz")
    line_sig_2.set_label(f"Componente ~ {f2:.1f} Hz")

    ax.set_xlim(0, len(y1))

    all_vals = np.concatenate([y1, y2])
    ymin = np.min(all_vals)
    ymax = np.max(all_vals)
    ax.set_ylim(ymin * 0.9, ymax * 1.1)

    ax.legend(loc="lower right")
    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

