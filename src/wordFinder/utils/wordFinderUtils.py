import time
from typing import Callable, Any, TypeVar, Optional

import core

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


def storeConfig(descriptionName: str) -> Callable[..., F]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:

            result = func(*args, **kwargs)

            # Avoid path overwrite if the result is an empty string.
            if result != '':
                core.storeConfig(descriptionName, result)

            return result
        return wrapper
    return decorator
