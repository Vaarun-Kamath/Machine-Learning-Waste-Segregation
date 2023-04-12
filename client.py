import socket
import threading
import pickle
import os
import time
import struct
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

motor = GPIO.PWM(11, 50)
motor.start(0)
time.sleep(2)


HEADER=1024
PORT=10050
SERVER="192.168.89.239"
ADDR=(SERVER,PORT)

def turn_servo(x:int, /)->None:
	global angle
	angle = x*60
	print(f'\x1b[41m{angle = }\x1b[0m')
	motor.ChangeDutyCycle(2+angle/18)
	time.sleep(0.5)
	#motor.ChangeDutyCycle(0)

def listen():
	with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
		print(client.connect(ADDR))
		payload_size=struct.calcsize("Q")
		print("hello")
		while True:
			os.system("fswebcam img.jpg")
			with open("img.jpg","rb") as file:
				a=pickle.dumps(file.read())
			message=struct.pack("Q",len(a))+a
			client.sendall(message)
			output=int(client.recv(HEADER).decode())
			turn_servo(output)
			print(f"\t\x1b[42m{output}\x1b[0m")


if __name__ == "__main__":
	listen()

