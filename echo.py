import socket
import sys

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 9999  # Arbitrary non-privileged port


def echo_process():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    try:
        s.bind((HOST, PORT))
    except:
        sys.exit()

    print('Socket bind complete')

    s.listen(1000)

    print('Socket now listening')

    # now keep talking with the client
    while 1:
        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

        while True:
            data = conn.recv(1024)
            reply = 'OK...' + data.decode()
            if not data:
                break
            conn.sendall(reply.encode())


while (True):
    try:
        echo_process()
    except:
        pass
