from time import time

class timeClass:
    def __init__(self, log,name ):
        self.log = log
        self.name =  name
        self.start_time = time()
    
    def end(self):
        self.elapsed_time = time() - self.start_time
        self.log.info(self.name+"=>words_existe time: %.10f seconds." % self.elapsed_time,True,True)
        return self.elapsed_time