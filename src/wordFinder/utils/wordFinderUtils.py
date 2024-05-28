import os
import json
import time
from typing import Callable, Any, TypeVar, Optional


DEV_MODE = False


F = TypeVar('F', bound=Callable[..., Any])

def devMode(dec: Callable[[Callable[..., Any]], F]) -> Callable[..., F]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            if not DEV_MODE:
                return func(*args, **kwargs)
            return dec(func)(*args, **kwargs)
        return wrapper
    return decorator


def timed(function: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        print(f"Function {function.__name__} executed in {end - start:.4f} sc")

        return result
    return wrapper


def searchPath() -> Optional[str]:
    """Gets the __search_path__ value from the config.json.

    Returns:
        The actual search path.
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as readFile:
        settings = json.load(readFile)
        return settings.get('__search_path__', None)


def addSearchPath(path: str) -> None:
    """Dumps the provided path to the config.json.

    Parameters:
        path: The path to dump.
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as readFile:
        settings = json.load(readFile)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'w') as writeFile:
        settings['__search_path__'] = path
        json.dump(settings, writeFile, indent=4)
