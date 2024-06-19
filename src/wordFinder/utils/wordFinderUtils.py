import time
from typing import Callable, Any, TypeVar

from wordFinder import core


DEV_MODE = False


F = TypeVar('F', bound=Callable[..., Any])


def devMode(dec: Callable[[Callable[..., Any]], F]) -> Callable[..., F]:
    """This is a decorator which can be transparent if the DEV_MODE constants is set to False.

    dec: The decorator to use.

    Returns:
        The function if :const:`DEV_MODE` is False, else, the decorator.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            if not DEV_MODE:
                return func(*args, **kwargs)
            return dec(func)(*args, **kwargs)
        return wrapper
    return decorator


def timed(function: Callable[..., Any]) -> Callable[..., Any]:
    """"A decorator to time the execution of a function"""
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        print(f"Function {function.__name__} executed in {end - start:.4f} sc")

        return result
    return wrapper


def storeConfig(configurationKey: str) -> Callable[..., F]:
    """This decorator will store the provided :param:`descriptionName` in the config.json.

    configurationKey: The key to store in the config.json.

    Notes:
        The value of the :param:`configurationKey` is the return value of the decorated function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:

            result = func(*args, **kwargs)

            # Avoid path overwrite if the result is an empty string.
            if result != '':
                core.storeConfig(configurationKey, result)

            return result
        return wrapper
    return decorator
