import socket

HOST = '0.0.0.0'
PORT = 9999

last_socket = None


def start_echo():
    global last_socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        last_socket = s

        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                conn.sendall(data)


while True:
    try:
        start_echo()
        last_socket.close()
    except:
        pass
