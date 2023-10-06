import socket

# Membuat socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Menghubungkan socket ke alamat dan port server
server_address = ('127.0.0.1', 5000)
client_socket.connect(server_address)

try:
    # Mengirim data ke server
    message = 'Halo server!'
    client_socket.sendall(message.encode())
    print('Pesan terkirim: {}'.format(message))

    # Menerima respons dari server
    response = client_socket.recv(5000)
    print('Menerima respons: {}'.format(response.decode()))

finally:
    # Menutup koneksi
    client_socket.close()
    print('Koneksi ditutup')
