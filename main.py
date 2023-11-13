import socket
import threading
import pickle
from datetime import datetime


def check_port(host_address: str, host_port: int, opens_obj: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        host, host_port = s.getpeername()

        opens_obj.add(f"{host}:{host_port}")
    except:
        pass


def fetch_them(min_num=0, max_num=102, min_port=555, max_port=555):
    opens = set()
    threads = []

    for num in range(min_num, max_num + 1):
        for port_num in range(min_port, max_port + 1):
            address = f"s{num}.serspeed.info"
            address = '82.115.17.99'
            thread = threading.Thread(target=check_port, args=(address, port_num, opens))
            threads.append(thread)
            thread.start()

    for i in range(min_num, max_num):
        threads[i].join()

    return opens


a = fetch_them(1, 1, 1, 3333)

# current_date_and_time_str = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')

# with open(f"opens {current_date_and_time_str}.pickle", "wb") as outfile:
#     pickle.dump(a, outfile)


# with open('opens 2022.12.28 08.02.00.581927.pickle', 'rb') as inputfile:
#     a = pickle.load(inputfile)

for i in a:
    print(i)
