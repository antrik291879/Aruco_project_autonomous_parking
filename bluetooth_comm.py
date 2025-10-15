import serial
import time

bluetooth = serial.Serial('COM5', 9600)
time.sleep(2) 


def send_command(cmd):
    bluetooth.write(cmd.encode())
    print(f"Sent: {cmd}")

while True:
    cmd1=input('character: ')
    send_command(cmd1)