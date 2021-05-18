import logging

_LOGGER = logging.getLogger(__name__)

def retry(howmany):
    def tryIt(func):
        def f(*args, **kwargs):
            last_exception = None
            attempts = 0
            while attempts < howmany:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e
            else:
                _LOGGER.warning(f'{howmany} attempts of {func.__name__} failed. Reason: {last_exception}')

        return f
    return tryIt
