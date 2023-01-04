import socket
import time
from concurrent.futures import ThreadPoolExecutor, wait
import pickle
from datetime import datetime

total_targets = 0


def check_port(host_address: str, host_port: int, opens: set):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_address, host_port))

        opens.add("{}:{}".format(host_address, host_port))
        print("{}:{}".format(host_address, host_port))
    except:
        pass


def fetch_them(domain_name_part_country_prefix: set, domain_name_part_number: set, ports: set,
               thread_pool_size: int = 100):
    global total_targets

    targets = set()
    futures = list()
    opens = set()

    for name_prefix in domain_name_part_country_prefix:
        for name_num in domain_name_part_number:
            for port_num in ports:
                address = "{}{}.nordvpn.com".format(name_prefix, name_num)
                targets.add((address, port_num))

    total_targets = len(targets)

    executor = ThreadPoolExecutor(thread_pool_size)

    for target in targets:
        futures.append(executor.submit(check_port, target[0], target[1], opens))

    wait(futures)

    return opens


country_prefix = 'us'

start_timestamp = time.time()
opens = fetch_them({country_prefix}, range(2000, 2002 + 1), {443}, 300)
finish_timestamp = time.time()

print("Took {} seconds to check {} targets".format(finish_timestamp - start_timestamp, total_targets))

current_date_and_time_str = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')

with open(f"nordvpn opens {country_prefix} {current_date_and_time_str}.pickle", "wb") as outfile:
    pickle.dump(opens, outfile)
