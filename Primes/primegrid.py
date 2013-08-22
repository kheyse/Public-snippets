
class Primegrid:
    def __init__(self,size):
        self.size = size
        self.grid = [True for i in xrange(self.size+1)]
        self.grid[0] = False
        self.grid[1] = False
        self.setup()
    def setup(self):
        for i in xrange(2,self.size):
            if self.grid[i]:
                start = i*i
                if start > self.size:
                    break
                for runner in xrange(start,self.size+1,i):
                    self.grid[runner] = False
    def isPrime(self,p):
        return self.grid[p]
    def __str__(self):
        return ','.join(map(str,self.list()))
    def list(self):
        return [i for i,v in enumerate(self.grid) if v]
    def iterate(self,start=0):
        return (i for i,v in enumerate(self.grid[start:],start) if v)
    def nextPrime(self,i):
        return next(self.iterate(i+1))


def primeTest(p):
    for i in xrange(2,int(sqrt(p))+1):
        if p%i==0:
            return False
    return True
        
