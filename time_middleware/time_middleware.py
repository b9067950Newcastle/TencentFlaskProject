import time

class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start_time = time.time()

        def new_start_response(status, headers, exc_info=None):
            elapsed = time.time() - start_time
            headers.append(('X-Response-Time', str(round(elapsed * 1000, 2))))
            return start_response(status, headers, exc_info)

        return self.app(environ, new_start_response)