import socket
import threading
import pickle
from datetime import datetime


def check_port(host_address: str, host_port: int, opens_obj: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        host, host_port = s.getpeername()

        opens_obj.add("{}:{}".format(host, host_port))
    except:
        pass


def fetch_them(min_num=0, max_num=102, min_port=0, max_port=1024):
    opens = set()
    threads = []

    for num in range(min_num, max_num + 1):
        for port_num in range(min_port, max_port + 1):
            address = "s{}.serspeed.info".format(num)
            thread = threading.Thread(target=check_port, args=(address, port_num, opens))
            threads.append(thread)
            thread.start()

    for i in range(min_num, max_num):
        threads[i].join()

    return opens


a = fetch_them(0, 1000, 1, 3333)

current_date_and_time_str = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')

with open(f"opens {current_date_and_time_str}.pickle", "wb") as outfile:
    pickle.dump(a, outfile)
