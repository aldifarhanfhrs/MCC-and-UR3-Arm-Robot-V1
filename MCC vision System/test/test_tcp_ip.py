import socket
import threading

host = "192.168.1.2"   # as both code is running on same pc
port = 5000  # socket server port number

def receive_response(client_socket):
    while True:
        try:
            # Menerima respons dari server
            response = client_socket.recv(1024)
            if response:
                print('Menerima respons: {}'.format(response.decode()))
        except:
            # Terjadi kesalahan, keluar dari loop
            break

client_socket = socket.socket()  # instantiate
client_socket.connect((host, port))  # connect to the server

response_thread = threading.Thread(target=receive_response, args=(client_socket,))
response_thread.start()
