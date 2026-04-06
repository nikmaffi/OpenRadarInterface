"""
    NAME:            Serial Communication Module (serial_comm/main.py)
    AUTHOR:          Nicolo' Maffi
    WRITTEN:         5 apr 2026
    COMPILED:        5 apr 2026
    INSTALLATION:    Linux Computer
"""

import serial
import signal
import time

# Specific module parameters
__SERIAL_PORT        = "/dev/ttyACM0"
__SERIAL_TIMEOUT     = 0.5            # Seconds
__SERIAL_DELAY_RECV  = 1e-3           # Seconds

# Firmware comm parameters
__SERIAL_BAUD_RATE = 115200
__SERIAL_STR_DEL   = "@"
__SERIAL_STOP_SIG  = "STOP"

# Close the serial port comm
def close_port(serial_port):
    if 'ser' in locals() and serial_port.is_open:
        serial_port.close()
        print(f"PORT {__SERIAL_PORT} CLOSED!")

# Module entry-point
def main():
    global serial_port

    print("SERIAL COMMUNICATION MODULE ONLINE!")

    try:
        serial_port = serial.Serial(
            port=__SERIAL_PORT,
            baudrate=__SERIAL_BAUD_RATE,
            timeout=__SERIAL_TIMEOUT
        )

        print(f"PORT {__SERIAL_PORT} INITIALIZED! LISTENING...")

        while True:
            try:
                # Checking buffer data
                if serial_port.in_waiting > 0:
                    line = serial_port.readline().decode('utf-8').strip()

                    # Check RADAR STOPPED signal
                    if line == __SERIAL_STOP_SIG:
                        print("RADAR HAS STOPPED!")
                    else:
                        distance, radians = line.split(__SERIAL_STR_DEL)
                        print(f"Distance {distance} cm at {radians} rad!")

                time.sleep(__SERIAL_DELAY_RECV)
            except (UnicodeDecodeError, ValueError):
                # Garbage data filter
                print("WARNING: SYNC ERROR OR CORRUPTED DATA RECEIVED!")
                continue
    except serial.SerialException:
        # Physical errors
        print(f"ERROR: CANNOT CONNECT TO {__SERIAL_PORT} PORT!")
    finally:
        close_port(serial_port)

# Signal handler manager
def signal_handler(sig, _):
    if sig in [signal.SIGHUP, signal.SIGINT]:
        close_port(serial_port)
        exit(-1)

    print("WARNING: CANNOT INTERRUPT THE MODULE!")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    main()
