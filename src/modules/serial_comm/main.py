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
import socket

__SERVER_ADDRESS     = "127.0.0.1"
__SERVER_PORT        = 21180

# Specific module parameters
__SERIAL_PORT        = "/dev/ttyACM0"
__SERIAL_TIMEOUT     = 0.5            # Seconds
__SERIAL_DELAY_RECV  = 1e-3           # Seconds

# Firmware comm parameters
__SERIAL_BAUD_RATE   = 115200

# Global comm resources
serial_port = None
sock = None

# Cleanup resources and exit
def close_all(code):
    global serial_port, sock

    if serial_port is not None and serial_port.is_open:
        serial_port.close()
        print(f"PORT {__SERIAL_PORT} CLOSED!")

    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            print("SOCKET CLOSED!")
        except OSError:
            # Socket already closed
            pass

    exit(code)

def socket_init():
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(None)

    try:
        sock.connect((__SERVER_ADDRESS, __SERVER_PORT))
    except ConnectionRefusedError:
        print(f"ERROR: CANNOT CONNECT TO {__SERVER_ADDRESS}:{__SERVER_PORT}!")
        close_all(-1)

# Module entry-point
def main():
    global serial_port, sock

    print("SERIAL COMMUNICATION MODULE ONLINE!")

    socket_init()

    try:
        serial_port = serial.Serial(
            port=__SERIAL_PORT,
            baudrate=__SERIAL_BAUD_RATE,
            timeout=__SERIAL_TIMEOUT
        )

        print(f"PORT {__SERIAL_PORT} INITIALIZED! LISTENING...")

        while True:
            try:
                if serial_port.in_waiting > 0:
                    sock.sendall(serial_port.readline())

                time.sleep(__SERIAL_DELAY_RECV)
            except ValueError:
                print("WARNING: CORRUPTED DATA RECEIVED!")
                continue
    except serial.SerialException:
        print(f"ERROR: CANNOT CONNECT TO {__SERIAL_PORT} PORT!")
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
