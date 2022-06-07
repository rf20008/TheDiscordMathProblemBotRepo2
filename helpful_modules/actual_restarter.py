import os
import threading
import time


def start():
    os.system("cd ../; python3.10 main.py")


t = threading.Thread(target=start)
time.sleep(5)
os._exit(0)
