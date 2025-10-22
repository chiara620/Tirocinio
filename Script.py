import serial
import time
from collections import deque
import matplotlib.pyplot as plt

PORT = "COM3"          
BAUD = 115200
BUFFER_SIZE = 100
FILE_PATH = "dati_arduino.csv"
TIMEOUT = 1

def open_serial(port, baud, timeout=0.1):
    ser = serial.Serial(port, baud, timeout=timeout)
    time.sleep(2)  # attesa reset Arduino
    ser.reset_input_buffer()
    return ser  # restituisco l'oggetto che farà la decodifica

def parse_line(line):   # Converte ogni riga bytes -> float
    try:
        s = line.decode('utf-8').strip()    #utf-8 è lo standard di decodifica (non ce ne sono altri)
        if not s:
            return None

        # esempio: "804 767"
        values = s.split()
        data = {}   #creo dizionario
        data = {f"A{i}": int(v) for i, v in enumerate(values)}
        return data if data else None
    
    except Exception:
        return None

def main():
    try:    # apertura seriale
        ser = open_serial(PORT, BAUD, TIMEOUT)
        print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")

        plt.ion()   # setup plotting
        fig, ax = plt.subplots()
        buffers = {}    # per gestione di più trimmer
        lines = {}
        ax.set_ylim(0, 1023)    #limite di arduino
        ax.set_xlabel("Campioni (ultimi N)")
        ax.set_ylabel("Valore analogico")
        ax.set_title("Lettura in tempo reale")

    except Exception as e:
        print(f"[ERRORE] Impossibile aprire {PORT}: {e}")
        return

    try:    # apertura file in append -> non perdo i valori precedenti
        f = open(FILE_PATH, "a")
        if f.tell() == 0:
            f.write("timestamp,pin,valore\n")   # intestazione file (solo se vuoto)
    except Exception as e:
        print(f"[ERRORE] Impossibile aprire file {FILE_PATH}: {e}")
        ser.close()
        return

    buffer = deque(maxlen=BUFFER_SIZE)
    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")

    try:
        while True:
            serial_line = ser.readline()
            v = parse_line(serial_line)
            if v is not None:
                ts = time.time()    # timestamp corrente
                for pin, value in v.items(): # una riga per ogni trimmer
                    buffer.append(value)    # appendo il valore per plottarlo
                    f.write(f"{ts},{pin},{value}\n")
                f.flush()  # assicura che i dati siano scritti subito
                print(f"{ts:.3f}: {v}")   # stampa su terminale x debugging

                for pin, value in v.items(): 
                    if pin not in buffers:  # se è la prima volta che compare questo trimmer, crea buffer e linea
                        buffers[pin] = deque(maxlen=BUFFER_SIZE)
                        (lines[pin],) = ax.plot([], [], label=pin)
                        ax.legend()
                    buffers[pin].append(value) # aggiorna buffer
                    xdata = range(len(buffers[pin]))    # aggiorna linea
                    ydata = list(buffers[pin])
                    lines[pin].set_data(xdata, ydata)
                if len(buffers) > 0: 
                    max_len = max(len(buf) for buf in buffers.values()) # sposta finestra per seguire asse x se arrivo a 100+
                    ax.set_xlim(max(0, max_len - BUFFER_SIZE), max_len) 
                plt.pause(0.01) # refresh


            else:
                plt.pause(0.01) # nessun dato valido -> passa oltre ma faccio comunque aggiornare il grafico

    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()
        f.close()
        print(f"[INFO] File salvato in: {FILE_PATH}")

if __name__ == "__main__":
    main()
