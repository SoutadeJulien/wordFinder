import os
import json
import time


DEV_MODE = False


def devMode(dec):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not DEV_MODE:
                return func(*args, **kwargs)
            return dec(func)(*args, **kwargs)
        return wrapper
    return decorator


def timed(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print(f"Function {function.__name__} executed in {end - start:.4f} sc")
    return wrapper


def searchPath():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as readFile:
        settings = json.load(readFile)
        return settings.get('__search_path__', None)


def addSearchPath(path):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as readFile:
        settings = json.load(readFile)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'w') as writeFile:
        settings['__search_path__'] = path
        json.dump(settings, writeFile, indent=4)
    return
