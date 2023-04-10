#server
import socket
import pickle
import struct
import threading

KB = 1024
CLOSED = 0
DRY = 1
RECYCLE = 2
WET = 3
decision = CLOSED
running = False
sent = False

def split_at(arr:list, x:int, /):
    return arr[:x], arr[x:]

def receiver(client_socket, client_address):
    global decision, sent
    print(f'{client_address[0]} [{client_address[1]}] joined')
    with client_socket:
        data = b""
        payload_size = struct.calcsize("Q")
        while running:
            data += client_socket.recv( 4 * KB )
            packed_msg_size, data = split_at( data, payload_size )
            msg_size = struct.unpack( "Q", packed_msg_size )
            while len(data) < msg_size:
                data += client_socket.recv(4 * KB)
            frame_data, data = split_at( data, msg_size )
            frame = pickle.loads(frame_data)
            #! calculations
            #! function must return 1: dry, 2: recyclable, 3: wet
            #!decision = function
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
        PORT = 10050
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

