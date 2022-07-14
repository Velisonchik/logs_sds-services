import datetime
import time

mas_exc = []
dict_exc = {}


def del_unwanted(d):
    with open('exc.txt', 'r') as exc:
        exc = exc.readlines()
        for v in d.values():
            for l in exc:
                if v in l:
                    del exc[exc.index(l)]
    with open('exc.txt', 'w') as f:
        f.writelines(exc)


def getfirstdigit(line):
    for i in list(line):
        if i.isdigit():
            return i
    return ''


def is_date(date):
    try:
        today = datetime.date.today().strftime('%y-%m-%d')
        valid_date = time.strptime(date, '%y-%m-%d')
        if date != today:
            return True
        else:
            return False
    except ValueError:
        return False


def clear():
    with open('exc.txt', 'r') as exc:
        exc = [i[0:i.index(' ')] for i in exc.readlines()]
        for l in exc:
            if l not in dict_exc.keys() and is_date(l[l.index(getfirstdigit(l)):l.index('.')]):
                dict_exc[l] = l[l.index(getfirstdigit(l)):l.index('.')]
    del_unwanted(dict_exc)
    # dict_exc = dict.fromkeys(mas_exc, '')


if __name__ == '__main__':
    clear()
