import matplotlib.pyplot as plt

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