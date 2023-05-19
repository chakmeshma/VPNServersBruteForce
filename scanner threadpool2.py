import socket
from concurrent.futures import ThreadPoolExecutor, wait
from timeit import default_timer as timer
import urllib3
import graceful_close

response_timeout = 10
connect_timeout = 10


# target_address = '45.35.50.219:55330'


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
                        break
                    else:
                        raise TimeoutError()

            except socket.error as e:
                if e.errno != socket.EWOULDBLOCK and e.errno != socket.EAGAIN:
                    raise TimeoutError()

        opens.add("{}:{}".format(host_address, host_port))
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


# def get_targets():
#     # with open('proxy-list-raw.txt', 'r') as feedfile:
#     #     feed_str = feedfile.read()
#
#     # with open('feed.txt', 'r') as feedfile:
#     #     feed_str2 = feedfile.read()
#
#     feed_resp = urllib3.request('GET',
#                                 'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt')
#     feed_str = feed_resp.data.decode('utf-8')
#     feed_list = feed_str.split('\n')
#
#     targets = set()
#
#     for tt in feed_list:
#         if tt.find(':') != -1:
#             tsp = tt.split(':')
#             tname = tsp[0]
#             tport = int(tsp[1])
#             targets.add((tname, tport))
#
#     return targets


def get_targets():
    # with open('proxy-list-raw.txt', 'r') as feedfile:
    #     feed_str = feedfile.read()

    with open('feed.txt', 'r') as feedfile:
        feed_str = feedfile.read()

    feed_list = feed_str.split('\n')

    targets = set()

    for tt in feed_list:
        if tt.find(':') != -1:
            tsp = tt.split(':')
            tname = tsp[0]
            tport = int(tsp[1])
            targets.add((tname, tport))

    return targets


with open('requestpduopenconnect.bin', 'rb') as requestbinfile:
    requestbin = requestbinfile.read()

# requestbin = requestbin.replace(b'sexhost', target_address.encode('ascii'))

targets = get_targets()

opens = fetch_them(targets, 100)

print("Found {}".format(len(opens)))
