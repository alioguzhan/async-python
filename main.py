import time
from multiprocessing import Pool
import grequests
import requests
from tornado import ioloop, httpclient

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
        self.tornado_counter = 0
        with open('urls.txt') as f:
            lines = f.readlines()
            self.urls = [line.strip('\n') for line in lines if len(line) > 5]

    def http_get(self, url):
        """ Common http get method """
        try:
            r = requests.get(url)
            r.raise_for_status()
        except:
            self.error_handler(r)

        return False

    @timeit
    def sync_reqs(self):
        print(green+'# Testing with NORMAL SYNCHRONOUS requests...'+reset)
        for url in self.urls:
            self.http_get(url)

        return False

    @timeit
    def async_reqs(self):
        print(green + '# Testing with ASYNCHRONOUS requests... [ MULTI-PROCESSING ] '+reset)
        proc_pool = Pool(processes=len(self.urls))
        # results = proc_pool.apply_async(self.http_get, self.urls)
        results = proc_pool.map(self.http_get, self.urls)
        return False
    
    @timeit
    def async_reqs_tornado(self):
        print('Testing with ASYNCHRONOUS requests... [ TORNADO ]')
        http_client = httpclient.AsyncHTTPClient()
        for url in self.urls:
            try:
                self.tornado_counter += 1
                r = http_client.fetch(url, self.request_callback,validate_cert=False)
            except httpclient.HTTPError as e:
                self.error_handler(r)

        ioloop.IOLoop.instance().start()
        return False

    @timeit
    def async_reqs_grequests(self):
        print(green + '# Testing with ASYNCHRONOUS requests... [ GREQUESTS ] ' + reset)
        reqs = [grequests.get(url) for url in self.urls]
        grequests.map(reqs, exception_handler=self.error_handler)
        return False

    def error_handler(self, request, *args, **kwargs):
        print(red + 'Request: %s -> Failed'%(request.url) + reset)

    
    def request_callback(self, response, *args, **kwargs):
        self.tornado_counter -= 1
        if response.error:
            print("Error: %s" % response.error)
        else:
            print(green + 'Database updated with response of ' + str(response.effective_url) + reset)

        if self.tornado_counter == 0:
            ioloop.IOLoop.instance().stop()


t = RequestTesting()
t.sync_reqs()
t.async_reqs()
t.async_reqs_tornado()
t.async_reqs_grequests()