import socket
from concurrent.futures import ThreadPoolExecutor, wait
from timeit import default_timer as timer
import graceful_close

response_start_timeout = 10
connect_timeout = 10
target_address = 'www.leader.ir:443'


def check_connect_and_connetverb(host_address: str, host_port: int, opens: set):
    global requestbin
    global response_start_timeout
    global connect_timeout
    # global accumulated_errors_set
    # global last_accerrlst_size

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
            if (timer() - response_start_timestamp) > response_start_timeout:
                raise TimeoutError()

            try:
                acc_inbound_response += s.recv(32)
                acc_inbound_response_str = acc_inbound_response.decode('ascii')

                if len(acc_inbound_response_str) >= 12 and acc_inbound_response_str[9:10] != '2':
                    raise TimeoutError()

                if acc_inbound_response_str.find('HTTP/1.1 2') == 0 or acc_inbound_response_str.find(
                        'HTTP/1.0 2') == 0:
                    break

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


def fetch_them(feed: str, thread_pool_size: int):
    targets = set()
    futures = list()
    opens = set()

    feed_list = feed.split('\n')

    for tt in feed_list:
        tsp = tt.split(':')
        tname = tsp[0]
        tport = int(tsp[1])
        # tport = 1666
        targets.add((tname, tport))

    executor = ThreadPoolExecutor(thread_pool_size)

    for target in targets:
        futures.append(executor.submit(check_connect_and_connetverb, target[0], target[1], opens))

    wait(futures)

    return opens


feedfile = open('proxy-list-raw.txt', 'r')
feed_str = feedfile.read()
feedfile.close()

requestbinfile = open('requestpdu2.bin', 'rb')
requestbin = requestbinfile.read()
requestbinfile.close()

requestbin = requestbin.replace(b'sexhost', target_address.encode('ascii'))

# last_accerrlst_size = -1
# accumulated_errors_set = dict()

opens = fetch_them(feed_str, 50)
