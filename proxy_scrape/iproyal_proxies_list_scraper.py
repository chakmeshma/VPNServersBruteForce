import socket
from concurrent.futures import ThreadPoolExecutor, wait


def check_port(host_address: str, host_port: int, opens: set):
    global requestbin
    global accumulated_errors_set
    global last_accerrlst_size

    s = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(True)
        s.settimeout(1000)

        s.connect((host_address, host_port))

        s.sendall(requestbin)

        responsebin = s.recv(10240)

        if len(responsebin) < 13:
            raise Exception('Not valid response (len < 13)')

        responsestr = responsebin.decode('ascii')

        response_header_str = responsestr.split('\r\n')[0]

        ccc = response_header_str.index('2')

        opens.add("{}:{}".format(host_address, host_port))
        print("{}:{}".format(host_address, host_port))
    except Exception as e:
        accumulated_errors_set[e.args] = e

        if len(accumulated_errors_set) != last_accerrlst_size:
            print(e)
            last_accerrlst_size = len(accumulated_errors_set)
    finally:
        if s:
            s.close()


def fetch_them(feed: str, thread_pool_size: int = 300):
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
        futures.append(executor.submit(check_port, target[0], target[1], opens))

    wait(futures)

    return opens


feedfile = open('../feed.txt', 'r')
feed_str = feedfile.read()
feedfile.close()

requestbinfile = open('../requestpdu.bin', 'rb')
requestbin = requestbinfile.read()
requestbinfile.close()

last_accerrlst_size = -1
accumulated_errors_set = dict()

opens = fetch_them(feed_str)
