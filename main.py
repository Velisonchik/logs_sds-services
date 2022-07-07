import os
import sys
import time
import yaml

import requests
from bot_req import *


def send_notification(msg_text):
    for gid in groups_id:
        url_req = "https://api.telegram.org/bot" + TOKEN + "/sendMessage" + "?chat_id=" + gid + "&text=" + msg_text
        results = requests.get(url_req)


def check_lines(test):
    global f
    for line in open('exc.txt', 'r').readlines():
        if test == line:
            return False
    return True


def scan_files(pdir):
    global f
    while True:
        ident_file = ''
        for pname in os.listdir(pdir):
            if os.path.isfile(pdir + '\\' + pname) and os.path.getmtime(pdir + '\\' + pname) - time.time() >= -100:
                with open(pdir + '\\' + pname, 'r') as f:
                    f = f.readlines()
                    for l in f:
                        ident_file = pdir + '\\' + pname + ' ' + l.replace('\n', '') + ' ' + str(f.index(l) + 1) + '\n'
                        if "error" in l and check_lines(ident_file):
                            if f.count(l) > 1:
                                open('exc.txt', 'a').write(ident_file)
                                send_notification(f'Ошибка в файле {pdir}+\\+{pname}, строка {f.index(l) + 1}')
                                f[f.index(l)] = ''
                                print(f)
                            else:
                                open('exc.txt', 'a').write(ident_file)
                                send_notification(f'Ошибка в файле {pdir}+\\+{pname}, строка {f.index(l) + 1}')
                                f[f.index(l)] = ''
                        else:
                            f[f.index(l)] = ''
            elif not os.path.isfile(pdir + '\\' + pname):
                scan_files(pdir + '\\' + pname)
        break


if __name__ == '__main__':
    open('exc.txt', 'a')
    try:
        path_dir = sys.argv[1]
        while True:
            scan_files(path_dir)
    except IndexError:
        print('Не указана директория с которой необходимо работать.')
        exit(1)
