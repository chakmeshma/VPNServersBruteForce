import socket


def _graceful_socket_close(s: socket.socket):
    if s:
        try:
            s.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            s.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(True)
s.settimeout(2)

try:
    s.connect(('www.google.com', 80))
except TimeoutError as e:
    print(e)
finally:
    _graceful_socket_close(s)
