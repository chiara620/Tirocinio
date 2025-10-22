import serial
import time
from collections import deque

PORT = "COM3"          
BAUD = 115200
BUFFER_SIZE = 100
FILE_PATH = "dati_arduino.csv"
TIMEOUT = 1

def open_serial(port, baud, timeout=1):
    ser = serial.Serial(port, baud, timeout=timeout)
    time.sleep(2)  # attesa reset Arduino
    ser.reset_input_buffer()
    return ser  # restituisco l'oggetto che farà la decodifica

def parse_line(line):   # Converte ogni riga bytes -> float
    try:
        s = line.decode('utf-8').strip()    #utf-8 è lo standard di decodifica (non ce ne sono altri)
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

def main():
    try:    # apertura seriale
        ser = open_serial(PORT, BAUD, TIMEOUT)
        print(f"[INFO] Connesso a {PORT} @ {BAUD} baud.")
    except Exception as e:
        print(f"[ERRORE] Impossibile aprire {PORT}: {e}")
        return

    try:    # apertura file in append -> non perdo i valori precedenti
        f = open(FILE_PATH, "a")
        if f.tell() == 0:
            f.write("timestamp,valore\n")   # intestazione file (solo se vuoto)
    except Exception as e:
        print(f"[ERRORE] Impossibile aprire file {FILE_PATH}: {e}")
        ser.close()
        return

    buffer = deque(maxlen=BUFFER_SIZE)
    print("[INFO] Lettura in corso... (Ctrl+C per interrompere)\n")

    try:
        while True:
            line = ser.readline()
            v = parse_line(line)
            if v is not None:
                buffer.append(v)
                ts = time.time()    # timestamp corrente
                f.write(f"{ts},{v}\n")
                f.flush()  # assicura che i dati siano scritti subito
                print(f"{ts:.3f}: {v}") # stampa su terminale x debugging
            else:
                pass # nessun dato valido -> passa oltre

    except KeyboardInterrupt:
        print("\n[STOP] Interruzione da tastiera. Chiusura...")

    finally:
        ser.close()
        f.close()
        print(f"[INFO] File salvato in: {FILE_PATH}")

if __name__ == "__main__":
    main()
