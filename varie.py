import serial
import time
import signal
import sys
import warnings
import matplotlib
matplotlib.use("TkAgg")  # assicura compatibilità con Tkinter

def open_serial(port, baud, timeout=0.1):
    ser = serial.Serial(port, baud, timeout=timeout)
    time.sleep(2)
    ser.reset_input_buffer()
    return ser


def parse_line(line):
    try:
        s = line.decode('utf-8').strip()    # standard protocollo di arduino
        if not s:
            return None

        # da arduino ricevo valore tipo "804 767"
        values = s.split()
        data = {f"A{i}": int(v) for i, v in enumerate(values)}
        return data if data else None
    except Exception:
        return None

def setup_safe_exit():
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