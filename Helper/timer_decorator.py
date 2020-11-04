from time import perf_counter


def timer(method):
    """
    This is a decorator function which is used to find and print the runtime of a function
    :param method: Method on which decorator is called
    :return: Method
    """
    def timed(*args, **kw):
        start_time = perf_counter()
        result = method(*args, **kw)
        end_time = perf_counter()
        print('%r  %2.2f ms' % (method.__name__, (end_time - start_time) * 1000))
        return result

    return timed
