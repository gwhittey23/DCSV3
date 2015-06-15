from collections import deque
from json import loads
from kivy.compat import PY2

from kivy.network.urlrequest import UrlRequest
try:
    HTTPSConnection = None
    if PY2:
        from httplib import HTTPSConnection
    else:
        from http.client import HTTPSConnection
except ImportError:
    # depending the platform, if openssl support wasn't compiled before python,
    # this class is not available.
    pass

from kivy.clock import Clock
from kivy.weakmethod import WeakMethod


# list to save UrlRequest and prevent GC on un-referenced objects
g_requests = []

class CustomUrlRequest(UrlRequest):
    def __init__(self, url, on_success=None, on_redirect=None,
             on_failure=None, on_error=None, on_progress=None,
             req_body=None, req_headers=None, chunk_size=8192,
             timeout=None, method=None, decode=True, debug=False,
             file_path=None):
        super(UrlRequest, self).__init__()
        self._queue = deque()
        self._trigger_result = Clock.create_trigger(self._dispatch_result, 0)
        self.daemon = True
        self.on_success = WeakMethod(on_success) if on_success else None
        self.on_redirect = WeakMethod(on_redirect) if on_redirect else None
        self.on_failure = WeakMethod(on_failure) if on_failure else None
        self.on_error = WeakMethod(on_error) if on_error else None
        self.on_progress = WeakMethod(on_progress) if on_progress else None
        self.decode = decode
        self.file_path = file_path
        self._debug = debug
        self._result = None
        self._error = None
        self._is_finished = False
        self._resp_status = None
        self._resp_headers = None
        self._resp_length = -1
        self._chunk_size = chunk_size
        self._timeout = timeout
        self._method = method

        #: Url of the request
        self.url = url

        #: Request body passed in __init__
        self.req_body = req_body

        #: Request headers passed in __init__
        self.req_headers = req_headers

        # save our request to prevent GC
        g_requests.append(self)

        self.start()
    def decode_result(self, result, resp):
        '''Decode the result fetched from url according to his Content-Type.
        Currently supports only application/json.
        '''
        # Entry to decode url from the content type.
        # For example, if the content type is a json, it will be automatically
        # decoded.

        content_type = resp.getheader('Content-Type', None)
        if content_type is not None:
            try:
                return loads(result)
            except:
                return result

        return super(CustomUrlRequest, self).decode_result(self, result, resp)