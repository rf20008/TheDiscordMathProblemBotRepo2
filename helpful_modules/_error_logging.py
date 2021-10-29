import time, traceback, datetime
def log_error(error,file_path=""):
    if not isinstance(file_path, str):
        raise TypeError("file_path is not a string")
    if not isinstance(error,BaseException):
        raise TypeError("error is not an error")
    if file_path == "":
        now = datetime.datetime.now()
        file_path = "error_logs/" + str(now.year) + " " + str({
        1: "January",
        2: "Febuary,",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
        }[now.month]) + " " + str(now.day) + ".txt"
    e=traceback.format_exception(type(error),error,tb=error.__traceback__)
    try:
        with open(file_path, "a") as f:
            f.write(time.asctime())
            f.write("\n" * 2)
            f.write("".join([str(item) for item in e]))
            f.write("\n" * 2)
    except Exception as exc:
        raise Exception("***File path not found.... or maybe something else happened.... anyway please report this :)***") from exc
    return e
    
