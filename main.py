import time
import grequests
import requests
from tornado.httpclient import AsyncHTTPClient

reset='\033[0m'
bold='\033[01m'

red='\033[31m'
green='\033[32m'
orange='\033[33m'
blue='\033[34m'

def timeit(method):
    """ Our timer decorator to measure execution time of request methods. """
    def wrapper(*args, **kwargs):
        time_start = time.time()
        result = method(*args, **kwargs)
        time_end = time.time()
        print(blue+'Method:%r took: %s %2.4f sec %s' % \
          (method.__name__, orange, time_end-time_start, reset)+reset)
        print('#'*60)
        return result

    return wrapper


class RequestTesting():
    def __init__(self):
        with open('urls.txt') as f:
            lines = f.readlines()
            self.urls = [line.strip('\n') for line in lines if len(line) > 5]

    @timeit
    def sync_reqs(self):
        print(green+'# Testing with NORMAL SYNCHRONOUS requests...'+reset)
        for url in self.urls:
            try:
                r = requests.get(url)
                r.raise_for_status()
            except:
                self.error_handler(r)

        return False

    @timeit
    def async_reqs(self):
        print('Testing with ASYNCHRONOUS requests... [ BUILT-IN ] ')
        return False
    
    @timeit
    def async_reqs_tornado(self):
        print('Testing with ASYNCHRONOUS requests... [ TORNADO ]')
        return False

    @timeit
    def async_reqs_grequests(self):
        print(green + '# Testing with ASYNCHRONOUS requests... [ GREQUESTS ] ' + reset)
        reqs = [grequests.get(url) for url in self.urls]
        grequests.map(reqs, exception_handler=self.error_handler)
        return False

    def error_handler(self, request, *args, **kwargs):
        print(red + 'Request: %s -> Failed'%(request.url) + reset)


t = RequestTesting()
t.sync_reqs()
t.async_reqs()
t.async_reqs_tornado()
t.async_reqs_grequests()