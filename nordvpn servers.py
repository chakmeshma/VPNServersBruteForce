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


def fetch_them(domain_name_part_vars: set, ports: set, thread_pool_size: int = 30):
    targets = set()
    futures = list()
    opens = set()

    for name_part_var in domain_name_part_vars:
        for port_num in ports:
            address = "de{}.nordvpn.com".format(name_part_var)
            targets.add((address, port_num))

    executor = ThreadPoolExecutor(thread_pool_size)

    for target in targets:
        futures.append(executor.submit(check_port, target[0], target[1], opens))

    wait(futures)

    return opens


fetch_them(range(1, 3000), {443}, 50)

# print(opens)
