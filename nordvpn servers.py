import contextlib
import itertools
import socket
import time
from concurrent.futures import ThreadPoolExecutor, wait
import pickle
from datetime import datetime

total_targets = 0


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with contextlib.suppress(Exception):
        s.connect((host_address, host_port))

        opens.add(f"{host_address}:{host_port}")
        print(f"{host_address}:{host_port}")


def fetch_them(domain_name_part_country_prefix: set, domain_name_part_number: set, ports: set,
               thread_pool_size: int = 100):
    global total_targets

    targets = set()
    opens = set()

    for name_prefix, name_num in itertools.product(domain_name_part_country_prefix, domain_name_part_number):
        address = f"{name_prefix}{name_num}.nordvpn.com"
        for port_num in ports:
            targets.add((address, port_num))

    total_targets = len(targets)

    executor = ThreadPoolExecutor(thread_pool_size)

    futures = [
        executor.submit(check_port, target[0], target[1], opens)
        for target in targets
    ]
    wait(futures)

    return opens


country_prefix = 'us'

start_timestamp = time.time()
opens = fetch_them({country_prefix}, range(2000, 2002 + 1), {443}, 300)
finish_timestamp = time.time()

print(
    f"Took {finish_timestamp - start_timestamp} seconds to check {total_targets} targets"
)

current_date_and_time_str = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')

with open(f"nordvpn opens {country_prefix} {current_date_and_time_str}.pickle", "wb") as outfile:
    pickle.dump(opens, outfile)
