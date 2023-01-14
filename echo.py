import socket

HOST = '0.0.0.0'
PORT = 9999

def start_echo():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
    except:
        pass
