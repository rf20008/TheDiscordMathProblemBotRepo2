import time, traceback
def log_error(error,file_path):
    if not isinstance(file_path, str):
        raise TypeError("file_path is not a string")
    if not isinstance(error,BaseException):
        raise TypeError("error is not an error")
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
    
