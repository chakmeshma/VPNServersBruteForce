import json
import os.path
import pickle
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from timeit import default_timer as timer
import urllib3
import graceful_close

target_address = 'www.facebook.com:443'
response_timeout = 20
connect_timeout = 20
thread_pool_size = 200
results_file_name = 'results'


def append_opens_result_file(target: tuple, file_lock):
    global results_file_name

    with file_lock:
        if not os.path.isfile(results_file_name) or os.path.getsize(results_file_name) == 0:
            with open(results_file_name, 'wb') as file_obj:
                pickle.dump(set(), file_obj)

        with open(results_file_name, 'rb') as file_obj:
            current_opens = pickle.load(file_obj)

        current_opens.add(target)

        with open(results_file_name, 'wb') as file_obj:
            pickle.dump(current_opens, file_obj)


def check_connect_and_connetverb(host_address: str, host_port: int, opens: set, file_lock):
    global requestbin
    global response_timeout
    global connect_timeout

    s = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(True)
        s.settimeout(connect_timeout)

        s.connect((host_address, host_port))

        s.sendall(requestbin)

        s.setblocking(False)

        acc_inbound_response = bytearray()

        response_start_timestamp = timer()

        while True:
            elapsed_time = timer() - response_start_timestamp
            if elapsed_time > response_timeout:
                raise TimeoutError()

            try:
                acc_inbound_response += s.recv(32)
                acc_inbound_response_str = acc_inbound_response.decode('ascii')

                if len(acc_inbound_response_str) >= 12:
                    if acc_inbound_response_str[9:10] == '2':
                        # print(acc_inbound_response_str)
                        break
                    else:
                        raise TimeoutError()

            except socket.error as e:
                if e.errno != socket.EWOULDBLOCK and e.errno != socket.EAGAIN:
                    raise TimeoutError()

        opens.add("{}:{}".format(host_address, host_port))
        # if host_port == 443:
        append_opens_result_file((host_address, host_port), file_lock)
        print("{} {}".format(host_address, host_port))
    except TimeoutError as e:
        pass
    finally:
        if s:
            graceful_close.graceful_socket_close(s)


def fetch_them(targets: set, thread_pool_size: int):
    futures = list()
    opens = set()

    executor = ThreadPoolExecutor(thread_pool_size)

    file_lock = threading.Lock()

    for target in targets:
        futures.append(executor.submit(check_connect_and_connetverb, target[0], target[1], opens, file_lock))

    wait(futures)

    return opens


def parse_feed(feed_str: str):  # feed has to be at least two lines (at least one newline present in file)
    feed_list = feed_str.splitlines()

    targets = set()

    for feed_item in feed_list:
        if 0 < feed_item.find(':') < len(feed_item) - 1:
            feed_item_splitted = feed_item.split(':')
            address = feed_item_splitted[0]
            port = int(feed_item_splitted[1])
            targets.add((address, port))

    return targets


def get_targets_url(url: str):
    feed_resp = urllib3.request('GET', url)

    is_utf8 = True

    try:
        content_type = feed_resp.headers.get('Content-Type')
        content_type.lower().index('utf-8')
    except Exception as e:
        is_utf8 = False

    feed_str = feed_resp.data.decode('utf-8' if is_utf8 else 'ascii')

    return parse_feed(feed_str)


def get_targets_file(file_name: str):
    with open(file_name, 'r') as feedfile:
        feed_str = feedfile.read()

    return parse_feed(feed_str)


def get_targets_file_json(file_name: str):
    with open(file_name, 'rb') as feedfile:
        feed_bin = feedfile.read()

    feed_str = feed_bin.decode('utf-8')

    json_file_data = json.loads(feed_str)['data']

    targets = set()

    for json_file_data_item in json_file_data:
        targets.add((json_file_data_item['ip'], int(json_file_data_item['port'])))

    return targets


with open('requestpdu_sexhost.bin', 'rb') as requestbinfile:
    requestbin = requestbinfile.read()
requestbin = requestbin.replace(b'sexhost', target_address.encode('ascii'))
# requeststr = requestbin.decode('ascii')

targets = set()
targets.update(get_targets_file('C:\\Users\\Chakmeshma\\Downloads\\http_proxies (4).txt'))
# targets.update(get_targets_file_json('feed.json'))
# targets.update(get_targets_file_json('feed2.json'))
# targets.update(get_targets_file('feed.txt'))
# targets.update(get_targets_file('feed2.txt'))
# targets.update(get_targets_file('feed3.txt'))
# targets.update(get_targets_file('feed4.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt'))
# targets.update(get_targets_url('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt'))

print("{} targets compiled".format(len(targets)))

opens = fetch_them(targets, thread_pool_size)

print("Found {}".format(len(opens)))
