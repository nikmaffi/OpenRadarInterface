"""
    NAME:            Serial Communication Module (serial_comm/main.py)
    AUTHOR:          Nicolo' Maffi
    WRITTEN:          5 apr 2026
    COMPILED:        11 apr 2026
    INSTALLATION:    Linux Computer
"""

import serial
import signal
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from radar_interface.interface import RadarInterface

# Specific module parameters
__SERIAL_PORT        = "/dev/ttyACM0"
__SERIAL_TIMEOUT     = 0.5            # Seconds
__SERIAL_DELAY_RECV  = 1e-3           # Seconds

# Firmware comm parameters
__SERIAL_BAUD_RATE   = 115200

# Global comm resources
serial_port = None

# Cleanup resources and exit
def close_all(code):
    global serial_port

    if serial_port is not None and serial_port.is_open:
        serial_port.close()
        print(f"PORT {__SERIAL_PORT} CLOSED!")

    exit(code)

# Module entry-point
def main():
    global serial_port

    print("SERIAL COMMUNICATION MODULE ONLINE!")

    radar_ui = RadarInterface()

    print("USER INTERFACE ONLINE!")

    try:
        serial_port = serial.Serial(
            port=__SERIAL_PORT,
            baudrate=__SERIAL_BAUD_RATE,
            timeout=__SERIAL_TIMEOUT
        )

        print(f"PORT {__SERIAL_PORT} INITIALIZED! LISTENING...")

        pos = 0
        dist = -1

        while True:
            while serial_port.in_waiting > 0:
                line = serial_port.readline().decode("utf-8", errors="replace").strip()

                if line:
                    try:
                        parts = line.split("@")
                        dist = int(float(parts[0]))
                        pos = float(parts[1])
                        print(dist)
                    except:
                        continue

            if radar_ui.execute(pos, dist):
                close_all(0)

    except serial.SerialException:
        print(f"ERROR: CANNOT CONNECT TO {__SERIAL_PORT} PORT!")
    finally:
        close_all(-1)

# Signal handler
def signal_handler(sig, _):
    if sig in [signal.SIGHUP, signal.SIGINT]:
        close_all(0)

    print("WARNING: CANNOT INTERRUPT THE MODULE!")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    main()
