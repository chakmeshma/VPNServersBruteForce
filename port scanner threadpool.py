import socket
from concurrent.futures import ThreadPoolExecutor, wait


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # s.settimeout(1.)
        s.connect((host_address, host_port))

        opens.add(f"{host_address}:{host_port}")
        print(f"{host_address}:{host_port}")
    except Exception:
        s.close()


def fetch_them(target_name: str, ports: set, thread_pool_size: int = 100):
    opens = set()

    targets = {(target_name, port_num) for port_num in ports}
    executor = ThreadPoolExecutor(thread_pool_size)

    futures = [
        executor.submit(check_port, target[0], target[1], opens)
        for target in targets
    ]
    wait(futures)

    return opens


opens = fetch_them('92.255.139.206', range(65536), 200)
