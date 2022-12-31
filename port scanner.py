import socket
import threading


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        host, host_port = s.getpeername()

        s.shutdown()
        s.close()

        opens.add("{}:{}".format(host, host_port))
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


opens = fetch_them('www.leader.ir', 443, 443)

for the_open in opens:
    print(the_open)
