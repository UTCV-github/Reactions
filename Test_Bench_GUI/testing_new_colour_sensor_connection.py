import serial
import time

# Adjust the port and baud rate to match your firmware
ser = serial.Serial(
    port='COM9',   # e.g. 'COM3' on Windows
    baudrate=115200,        # match what's set in your sketch
    timeout=1
)

time.sleep(2)  # Give the board time to reset after connection

# Read incoming data
while True:
    ser.write(b'p')
    print("Writing p to board")
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print(f"Received: {line}")

    time.sleep(1)

# Send data to the board
ser.write(b'hello\n')

ser.close()