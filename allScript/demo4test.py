# coding=utf-8
import threading
import time


def testtread(num):
    print(f'{threading.current_thread()} 取走了 {num}')
    # time.sleep(0.1)


if __name__ == '__main__':
    proc_lsit = []
    for i in range(10):
        proc = threading.Thread(target=testtread, args=(i,))
        proc_lsit.append(proc)

    for k in proc_lsit:
        k.start()