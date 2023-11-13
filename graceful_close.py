import socket


def graceful_socket_close(s: socket.socket):
    if s:
        try:
            s.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        finally:
            s.close()
