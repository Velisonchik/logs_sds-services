import os
import sys
import sqlite3
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import threading
from bot_req import *

excs = ("declare error_code", "ignore error code")
paths_to_scan = []


class OnMyWatch:
    # Set the directory on watch

    def __init__(self, path):
        self.watchDirectory = path
        self.observer = Observer()

    def run(self):
        print(f'running on %s' % self.watchDirectory)
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(0.1)
        except Exception as e:
            self.observer.stop()
            print("Observer Stopped", e)

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now
            add_to_paths_to_scan(event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            add_to_paths_to_scan(event.src_path)


def add_to_paths_to_scan(path):
    print('add_to_paths_to_scan', path)
    global paths_to_scan
    if path not in paths_to_scan:
        paths_to_scan.append(path)


def manage_files_time():
    global paths_to_scan
    while True:
        if len(paths_to_scan) > 0:
            for i in paths_to_scan:
                if i != '':
                    time.sleep(1)
                    scan_file(i)
                    paths_to_scan[paths_to_scan.index(i)] = ''
            clear_paths_to_scan()


def clear_paths_to_scan():
    global paths_to_scan
    for i in paths_to_scan:
        if i == '':
            del paths_to_scan[paths_to_scan.index(i)]


def send_notification(msg_text):
    for gid in groups_id:
        try:
            if max_hour_notification >= datetime.datetime.now().hour >= min_hour_notification:
                url_req = "https://api.telegram.org/bot" + TOKEN + "/sendMessage" + "?chat_id=" + gid + "&parse_mode=HTML" \
                          + "&text=" + msg_text
                requests.get(url_req)
        except Exception as e:
            print(e)


def sqlite_insert(temp_f, len_f):
    try:
        sqlite_connection = sqlite3.connect(dbname)
        cursor = sqlite_connection.cursor()
        cursor.execute(f"INSERT or replace INTO exc values(NULL,'{temp_f}',{len_f});")
        sqlite_connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при insert к sqlite", error)


def sqlite_select_lastline(temp_f):
    try:
        sqlite_connection = sqlite3.connect(dbname)
        cursor = sqlite_connection.cursor()
        cursor.execute(f"SELECT last_readline FROM exc WHERE file_name='{temp_f}'")
        res = cursor.fetchone()
        cursor.close()
        if res is None:
            return -1
        else:
            return res[0]

    except sqlite3.Error as error:
        print("Ошибка при select к sqlite", error)


def is_exc(pl):
    global excs
    for i in excs:
        if i in pl:
            return True
    return False


def first_read(pname):
    if sqlite_select_lastline(pname) == -1:
        return True
    else:
        return False


def scan_file(pname):
    if pname.endswith('.txt') or pname.endswith('.log'):
        with open(pname, 'r') as f:
            f = f.readlines()
            len_f = len(f)
            if first_read(pname):
                sqlite_insert(pname, len_f)
            else:
                fname = pname[pname.rfind('\\') + 1:]
                dname = pname[:pname.rfind('\\')]
                template_head = f'<b>{fname}</b> ({dname})\n\n'
                msg = template_head
                start_line = sqlite_select_lastline(pname)
                for line in f[start_line:]:
                    if ("error" in line.lower() or "exception" in line.lower()) and not is_exc(line.lower()):
                        if len(msg + f'Cтрока: {f.index(line, start_line) + 1}\n{line}\n') > 4090:
                            send_notification(msg)
                            msg = template_head
                        else:
                            msg += f'Cтрока: {f.index(line, start_line) + 1}\n{line}\n'
                            f[f.index(line, start_line)] = ''
                    else:
                        f[f.index(line, start_line)] = ''
                sqlite_insert(pname, len_f)
                if msg != template_head:
                    send_notification(msg)


def con_DB():
    try:
        sqlite_connection = sqlite3.connect(dbname)
        cursor = sqlite_connection.cursor()
        print("База данных создана и успешно подключена к SQLite")
        sqlite_select_query = "CREATE TABLE IF NOT EXISTS exc (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," \
                              "file_name file_name TEXT NOT NULL, last_readline last_readline INTEGER NOT NULL,UNIQUE" \
                              " (file_name));"
        cursor.execute(sqlite_select_query)
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)


def watchdog_run(path):
    watch = OnMyWatch(path=path)
    watch.run()


if __name__ == '__main__':
    try:
        path_dirs = sys.argv[1].split(',')
        if not os.path.exists(dbname):
            with open(dbname, 'w') as _:
                pass
        con_DB()
    except IndexError:
        print('Не указана директория с которой необходимо работать.')
        exit(1)
    manage_files_time_thread = threading.Thread(target=manage_files_time)
    manage_files_time_thread.start()
    for path_dir in path_dirs:
        dir_thread = threading.Thread(target=watchdog_run, args=(path_dir,))
        dir_thread.start()
