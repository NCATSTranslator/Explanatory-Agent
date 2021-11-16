import requests
from multiprocessing import Process, Manager
import logging
import modConfig


def _request_runner(method, url, response_proxy, **kwargs):
    logging.basicConfig(level=modConfig.defaultLoggingLevel)
    response_proxy['response'] = requests.request(method, url, **kwargs)


def request_with_global_timeout(method, url, global_timeout, **kwargs):
    if global_timeout is None or global_timeout == 0:
        return requests.request(method, url, timeout=5*60, **kwargs)
        # return requests.request(method, url, timeout=3, **kwargs)
    manager = Manager()
    response_proxy = manager.dict()
    process = Process(
        target=_request_runner,
        args=(method, url, response_proxy),
        kwargs=kwargs
    )
    process.start()
    process.join(global_timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        raise requests.exceptions.Timeout
    return response_proxy['response']


if __name__ == '__main__':

    response = request_with_global_timeout(
        method="post",
        url="https://name-resolution-sri.renci.org/lookup",
        global_timeout=5,
        params={"string": "Aspirin", "offset": 0, "limit": 1}
    )


