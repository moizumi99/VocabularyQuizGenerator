import datetime
from pathlib import Path

def date():
    write(str(datetime.datetime.now()))

def write(txt):
    log_file = str(Path.cwd()) + "/log.txt"
    try:
        with open(log_file, 'a', encoding='utf8') as log_file:
            log_file.write(txt)
            log_file.write("\n")
    except IOError:
        pass

def getTime():
    time_log = "{:02d}:{:02d}:{:02d}".format(
        datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
    return time_log
    
def log(txt):
    write("LOG({}): {}".format(getTime(), txt))

def warn(txt):
    write("Warning({}): {}".format(getTime(), txt))

