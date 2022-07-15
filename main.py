import os
import sys
import time
import requests
import clear_exc
import threading
from bot_req import *

excs = ["declare error_code", "ignore error code"]


def send_notification(msg_text):
    for gid in groups_id:
        try:
            url_req = "https://api.telegram.org/bot" + TOKEN + "/sendMessage" + "?chat_id=" + gid + "&parse_mode=HTML" + "&text=" + msg_text
            results = requests.get(url_req)
        except Exception as e:
            print(e)


def is_exc(pl):
    global excs
    for i in excs:
        if i in pl:
            return True
    return False


def check_lines(test):
    for line in open('exc.txt', 'r').readlines():
        if test == line:
            return False
    return True


def scan_files(pdir):
    try:
        while True:
            ident_file = ''
            for pname in os.listdir(pdir):
                if os.path.isfile(pdir + '\\' + pname):
                    if pname.endswith('.txt') or pname.endswith('.log'):
                        if os.path.getmtime(pdir + '\\' + pname) - time.time() >= -100:
                            with open(pdir + '\\' + pname, 'r') as f:
                                template_head = f'<b>{pname}</b> ({pdir})\n\n'
                                msg = template_head
                                f = f.readlines()
                                for l in f:
                                    if "error" in l.lower() or "exception" in l.lower():
                                        ident_file = pdir + '\\' + pname + ' ' + l.replace('\n', '') + ' ' + str(
                                            f.index(l) + 1) + '\n'
                                        if check_lines(ident_file) and not is_exc(l.lower()):
                                            open('exc.txt', 'a').write(ident_file)
                                            if len(msg + f'Cтрока: {f.index(l) + 1}\n{l}\n') > 4090:
                                                send_notification(msg)
                                                msg = template_head
                                            else:
                                                msg += f'Cтрока: {f.index(l) + 1}\n{l}\n'
                                                # send_notification(f'<b>{pname}</b> ({pdir})\nCтрока: {f.index(l) + 1}\n{l}')
                                                f[f.index(l)] = ''
                                    else:
                                        f[f.index(l)] = ''
                            if msg != template_head:
                                send_notification(msg)
                elif not os.path.isfile(pdir + '\\' + pname):
                    scan_files(pdir + '\\' + pname)
            break
    except Exception as e:
        print(e)


def main(cell):
    with open(f'exc.txt', 'a'):
        pass
    try:
        while True:
            file_stats = os.stat('exc.txt')
            if file_stats.st_size / (1024 * 1024) > 2:
                clear_exc.clear()
            scan_files(cell)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        path_dirs = sys.argv[1].split(',')
    except IndexError:
        print('Не указана директория с которой необходимо работать.')
        exit(1)
    for path_dir in path_dirs:
        dir_thread = threading.Thread(target=main, args=(path_dir,))
        dir_thread.start()
