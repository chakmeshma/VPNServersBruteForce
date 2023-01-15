import socket
from concurrent.futures import ThreadPoolExecutor, wait


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        opens.add("{}:{}".format(host_address, host_port))
        print("{}:{}".format(host_address, host_port))
    except:
        pass


def fetch_them(target_name: str, ports: set, thread_pool_size: int = 100):
    targets = set()
    futures = list()
    opens = set()

    for port_num in ports:
        targets.add((target_name, port_num))

    executor = ThreadPoolExecutor(thread_pool_size)

    for target in targets:
        futures.append(executor.submit(check_port, target[0], target[1], opens))

    wait(futures)

    return opens


opens = fetch_them('192.168.1.100', range(0, 65536), 200)
