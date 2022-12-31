import socket
import threading
import time


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        host, host_port = s.getpeername()

        s.shutdown(socket.SHUT_RDWR)
        s.close()

        open_str = "{}:{}".format(host, host_port)

        opens.add(open_str)

        print(open_str)
    except:
        pass


def fetch_them(address_name: str, min_port=0, max_port=65535):
    opens = set()
    threads = []

    for port in range(min_port, max_port + 1):
        thread = threading.Thread(target=check_port, args=(address_name, port, opens))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return opens


start_timestamp = time.time()
opens = fetch_them('www.leader.ir')
finish_timestamp = time.time()

print("Took {} seconds".format(finish_timestamp - start_timestamp))

# for the_open in opens:
#     print(the_open)
