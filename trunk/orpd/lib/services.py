import threading

class Service(object):
    def __call__(self, *args, **kwargs):
        return self.start(*args, **kwargs)
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = False
    
    def __go(self):
        while self.running:
            self.func(*self.args, **self.kwargs)

    def start(self, *args, **kwargs):
        self.running = True
        if args:
            self.args = args
        if kwargs:
            self.kwargs = kwargs
        self.proc = threading.Thread(target=self.__go)
        self.proc.start()
    
    def toggle(self, *args, **kwargs):
        if self.running:
            self.running = False
        else:
            return self.start(*args, **kwargs)
    
    def stop(self):
        self.running = False

def service(func, *args, **kwargs):
    result = Service(func, *args, **kwargs)
    return result