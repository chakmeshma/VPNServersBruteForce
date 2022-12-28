import socket
import time
import sys

import winsound


def check_port(host_address: str, host_port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        return True
    except:
        return False


target_name = sys.argv[1]
target_port = int(sys.argv[2])

while not check_port(target_name, target_port):
    time.sleep(1)

winsound.Beep(1666, 6666)
