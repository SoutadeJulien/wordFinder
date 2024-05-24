import time

def timed(function):
    def wrapper(*args, **kwargs):
        start = time.time()

        result = function(*args, **kwargs)

        end = time.time()

        print(f"Function {function.__name__} executed in {end - start:.4f} sc")
        return result
    return wrapper
