import json
import socket
from concurrent.futures import ThreadPoolExecutor, wait
from timeit import default_timer as timer
import urllib3
import graceful_close

response_timeout = 30
connect_timeout = 30

target_address = 'www.facebook.com:443'


def check_connect_and_connetverb(host_address: str, host_port: int, opens: set):
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

    for target in targets:
        futures.append(executor.submit(check_connect_and_connetverb, target[0], target[1], opens))

    wait(futures)

    return opens


def parse_feed(feed_str: str):
    if feed_str.find('\n\a') != -1:
        feed_delimieter = '\n\a'
    elif feed_str.find('\n') != -1:
        feed_delimieter = '\n'
    else:
        raise Exception()

    feed_list = feed_str.split(feed_delimieter)

    targets = set()

    for tt in feed_list:
        if 0 < tt.find(':') < len(tt) - 1:
            tsp = tt.split(':')
            tname = tsp[0]
            tport = int(tsp[1])
            targets.add((tname, tport))

    return targets


def get_targets_url(url: str):
    feed_resp = urllib3.request('GET', url)
    feed_str = feed_resp.data.decode('utf-8')

    return parse_feed(feed_str)


def get_targets_file(file_name: str):
    with open(file_name, 'r') as feedfile:
        feed_str = feedfile.read()

    return parse_feed(feed_str)


def get_targets_file_json(file_name: str):
    with open(file_name, 'rb') as feedfile:
        feed_bin = feedfile.read()

    feed_str = feed_bin.decode('utf-8')

    zzz = json.loads(feed_str)['data']

    targets = set()

    for i in zzz:
        targets.add((i['ip'], int(i['port'])))

    return targets


with open('requestpdu_sexhost.bin', 'rb') as requestbinfile:
    requestbin = requestbinfile.read()
requestbin = requestbin.replace(b'sexhost', target_address.encode('ascii'))
# requeststr = requestbin.decode('ascii')

targets = set()
targets.update(get_targets_file_json('feed.json'))
targets.update(get_targets_file_json('feed2.json'))
targets.update(get_targets_file('feed.txt'))
targets.update(get_targets_file('feed2.txt'))
targets.update(get_targets_file('feed3.txt'))
targets.update(get_targets_file('feed4.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt'))
targets.update(get_targets_url('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt'))

opens = fetch_them(targets, 150)

print("Found {}".format(len(opens)))
