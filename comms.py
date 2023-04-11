#server
import socket
import pickle
import numpy as np
import time
import struct
from keras.models import load_model
import random
import threading
import cv2 as cv


KB = 1024
CLOSED = 0
DRY = 1
RECYCLE = 2
WET = 3
PORT = 10050
decision = CLOSED
running = False
sent = False
model = load_model("keras_Model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()

def split_at(arr:list, x:int, /):
    return arr[:x], arr[x:]

def receiver(client_socket, client_address):
    global decision, sent
    print(f'{client_address[0]} [{client_address[1]}] joined')
    with client_socket:
        data = b""
        payload_size = struct.calcsize("Q")
        while running:
            while len(data) < payload_size:
                data += client_socket.recv( 4 * KB )
            packed_msg_size, data = split_at( data, payload_size )
            msg_size = struct.unpack( "Q", packed_msg_size )[0]
            while len(data) < msg_size:
                data += client_socket.recv(4 * KB)
            frame_data, data = split_at( data, msg_size )
            frame = pickle.loads(frame_data)
            with open('IMG.jpg','wb') as f:
                f.write(frame)
                # decision = int(time.time())
            #! calculations
            #! function must return 1: dry, 2: recyclable, 3: wet
            #!decision = function

            # Predicts the model
            image = cv.imread('IMG.jpg')
            image = cv.resize(image, (224, 224), interpolation=cv.INTER_AREA)

            # Make the image a numpy array and reshape it to the models input shape.
            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
            #
            # # Normalize the image array
            image = (image / 127.5) - 1
            prediction = model.predict(image)

            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]
            # decision = int(class_name[0]) ########!!!!!!!!! UN COMMENT THIS PLS :)
            # decision = random.randint(0,3)
            decision = 2
            print("---------------------------------------------")
            print(f"Confidence Sent: {confidence_score}")
            print(f"Classification Sent : {class_name[2:]}")
            print("---------------------------------------------")
            # Print prediction and confidence score
            # keyboard_input = cv.waitKey(1)
            # 27 is the ASCII for the esc key on your keyboard.
            # if keyboard_input == 27:
            #     print("Class:", class_name[2:], end="")
            #     # print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
            #     decision = int(class_name[0])
            #     running = False
                # socket.close(client_socket)
                # break
            sent = False

def sender(client_socket, client_address):
    global sent
    while running:
        if sent: continue
        client_socket.send(f'{decision}'.encode())
        sent = True

def startup():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sckt:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print(f'HOST NAME:{host_name}[{host_ip}]')
        socket_address = (host_ip, PORT)
        print('Socket created', end='')
        server_sckt.bind(socket_address)
        print(', Bound', end='')
        server_sckt.listen(5)
        print('and listening')
        client_socket, client_address = server_sckt.accept()
        rcv_t = threading.Thread(target=receiver, args=(client_socket, client_address))
        snd_t = threading.Thread(target=sender, args=(client_socket, client_address),daemon=True)
        rcv_t.start()
        snd_t.start()
        rcv_t.join()


if __name__ == "__main__":
    running = True
    startup()

