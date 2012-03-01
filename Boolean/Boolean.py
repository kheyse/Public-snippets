#!/usr/bin/env python

class Op:
    def isValidPOS(self):
        return True
    def copy(self):
        return self
    def clean(self):
        return self
    def simplify(self):
        return self
    def canonicalise(self):
        return self
    def reduceNotOps(self):
        return self
    def reduceToPOS(self):
        return self
    def simplifyPOS(self):
        return self
    def evaluate(self,val):
        return self
    def satsolvePOS(self):
        return (self,[])
    isValidSOP=isValidPOS
    reduceToSOP=reduceToPOS
    simplifySOP=simplifyPOS
    
def compareSize(o1,o2):
	return cmp(o1.size(),o2.size())

def compareOp(o1,o2):
    while isinstance(o1,NotOp):
        o1=o1.op
    while isinstance(o2,NotOp):
        o2=o2.op
    if isinstance(o1,AndOp):
        if isinstance(o2,AndOp):
            if len(o1.ops)<len(o2.ops):
                return -1
            elif len(o1.ops)>len(o2.ops):
                return 1
            else:
                for i in xrange(len(o1.ops)):
                    res=compareOp(o1.ops[i],o2.ops[i])
                    if res!=0:
                        return res
                return 0
        else:
            return 1
    elif isinstance(o1,OrOp):
        if isinstance(o2,AndOp):
            return -1
        elif isinstance(o2,OrOp):
            if len(o1.ops)<len(o2.ops):
                return -1
            elif len(o1.ops)>len(o2.ops):
                return 1
            else:
                for i in xrange(len(o1.ops)):
                    res=compareOp(o1.ops[i],o2.ops[i])
                    if res!=0:
                        return res
                return 0
        else:
            return 1
    elif isinstance(o1,VarOp):
        if isinstance(o2,TrueOp):
            return 1
        elif isinstance(o2,VarOp):
            res=cmp(o1.name,o2.name)
            if res!=0:
                return res
            else:
                return 0
        else:
            return -1
    elif isinstance(o1,TrueOp):
        if isinstance(o2,TrueOp):
            return 0
        else:
            return -1

def sumImplies(o1,o2):
    if isinstance(o1,VarOp) or isinstance(o1,NotOp):
        if isinstance(o2,VarOp) or isinstance(o2,NotOp):
            return o1==o2
        else:
            return o1 in o2.ops
    assert isinstance(o1,OrOp)
    assert isinstance(o2,OrOp)
    assert len(o1.ops)<=len(o2.ops)
    for oa in o1.ops:
        if oa not in o2.ops:
            return False
    return True 
        
def productImplies(o1,o2):
    if isinstance(o1,VarOp) or isinstance(o1,NotOp):
        if isinstance(o2,VarOp) or isinstance(o2,NotOp):
            return o1==o2
        else:
            return o1 in o2.ops
    assert isinstance(o1,AndOp)
    assert isinstance(o2,AndOp)
    assert len(o1.ops)<=len(o2.ops)
    for oa in o1.ops:
        if oa not in o2.ops:
            return False
    return True 
    
class TrueOp(Op):
    def __init__(self):
        None
    def invert(self):
        return NotOp(self)
    def size(self):
    	return 0
    def __str__(self):
        return "1"
    def __eq__(self, other):
        if isinstance(other, TrueOp):
            return True
        else:
            return False


class VarOp(Op):
    def __init__(self,name):
        self.name=name
    def invert(self):
        return NotOp(self)
    def evaluate(self,val):
        value=val.get(self)
        if value!=None:
            return value
        else:
            return self
    def size(self):
    	return 1
    def __str__(self):
        return self.name

class NotOp(Op):
    def __init__(self,op):
        self.op=op
    def invert(self):
        return self.op
    def reduceNotOps(self):
        if not (isinstance(self.op, VarOp) or isinstance(self.op, TrueOp)):
            return self.op.invert().reduceNotOps()
        else:
            return self
    def isValidPOS(self):
        return isinstance(self.op, VarOp) or isinstance(self.op, TrueOp)
    def simplify(self):
        self.op=self.op.simplify()
        if isinstance(self.op, NotOp):
            return self.op.op
        return self
    def reduceToPOS(self):
        if not (isinstance(self.op, VarOp) or isinstance(self.op, TrueOp)):
            print "Perform reduceNotOps() first"
        return self
    isValidSOP=isValidPOS
    reduceToSOP=reduceToPOS
    def evaluate(self,val):
        self.op=self.op.evaluate(val)
        return self.simplify()
    def satsolvePOS(self):
        if isinstance(self.op,TrueOp):
            return None
        else:
            return self
    def size(self):
    	return self.op.size()
    def copy(self):
        return NotOp(self.op.copy())
    def __str__(self):
        return str(self.op)+"!"
    def __eq__(self, other):
        if isinstance(other, NotOp):
            return self.op==other.op
        else:
            return False

class AndOp(Op):
    def __init__(self,ops):
        assert isinstance(ops,list)
        self.ops=ops
    def invert(self):
        return OrOp([NotOp(o) for o in self.ops])
    def reduceNotOps(self):
        return AndOp([o.reduceNotOps() for o in self.ops]).clean()
    def isValidPOS(self):
        for o in self.ops:
            if not o.isValidPOS():
                return False
        return True
    def isValidSOP(self):
        for o in self.ops:
            if isinstance(o, OrOp):
                return False
            elif not o.isValidSOP():
                return False
        return True
    def simplify(self): #recursive clean()
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].simplify()
        return self.clean()
    def clean(self):    #result is sorted by size
        varList=[]
        varInvertedList=[]
        i=0
        while i<len(self.ops):
            o=self.ops[i]
            if isinstance(o, AndOp): # a AND (b AND c) = a AND b AND c
                self.ops.extend(o.ops)
                self.ops.pop(i)
                i-=1
            elif isinstance(o, VarOp):
                if o in varList: # ... AND a AND a = ... AND a
                    self.ops.pop(i)
                    i-=1
                elif o in varInvertedList: # ... AND a AND !a = False
                    return NotOp(TrueOp())
                else:
                    varList.append(o)
            elif isinstance(o, TrueOp) and len(self.ops)>1: # f AND True = f
                self.ops.pop(i)
                i-=1
            elif isinstance(o, NotOp):
                if isinstance(o.op, VarOp):
                    if o.op in varList: # ... AND a AND !a = False
                        return NotOp(TrueOp())
                    elif o.op in varInvertedList: # ... AND a! AND a! = ... AND a!
                        self.ops.pop(i)
                        i-=1
                    else:
                        varInvertedList.append(o.op)
                elif isinstance(o.op, TrueOp):  # ... AND False = False
                    return NotOp(TrueOp())
            i+=1
        if len(self.ops)==1:
            return self.ops[0]
        self.ops.sort(compareSize)
        return self
    def reduceToPOS(self):  #simplify() first, result is simplify() and simplifyPOS()
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].reduceToPOS()
        return self.clean().simplifyPOS()
    def reduceToSOP(self):  #simplify() first, result is simplify() and simplifyPOS()
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].reduceToSOP()
        while len(self.ops)>=2: #distributivity
            o1=self.ops[-1]
            self.ops.pop(-1)
            if not isinstance(o1,OrOp):
                o1=OrOp([o1])
            o2=self.ops[-1]
            self.ops.pop(-1)
            if not isinstance(o2,OrOp):
                o2=OrOp([o2])
            andList=[AndOp([ob, oa]).clean() for oa in o1.ops for ob in o2.ops]
            res=OrOp(andList).clean().simplifySOP()
            self.ops.append(res)
        return self.clean()
    def canonicalise(self): #recursive sort
        for o in self.ops:
            o.canonicalise()
        self.ops.sort(compareOp)
        return self
    def simplifyPOS(self):  #simplify() first, result is simplify()
        i=0
        while i<len(self.ops):
            o1=self.ops[i]
            o1inv=o1.invert()
            j=i+1
            if isinstance(o1,VarOp) or isinstance(o1,NotOp):
                while j<len(self.ops):
                    o2=self.ops[j]
                    if isinstance(o2,VarOp) or isinstance(o2,NotOp):
                        j+=1
                    else:
                        if o1 in o2.ops: # a AND (a OR b OR c) = a
                            self.ops.pop(j)
                        else:
                            if o1inv in o2.ops: # a AND (a! OR b OR c) = a AND (b OR c)
                                o2.ops.remove(o1inv)
                                o2=o2.clean()
                                self.ops.pop(j)
                                k=i+1
                                while k<len(self.ops):
                                    if compareSize(o2,self.ops[k])==-1:
                                        self.ops.insert(k,o2)
                                        break
                                    k+=1
                                if k==len(self.ops):
                                    self.ops.append(o2)
                            j+=1
            else:
                while j<len(self.ops):
                    if sumImplies(o1,self.ops[j]): # (a OR b) AND (a OR b OR c OR d) = (a OR b)
                        self.ops.pop(j)
                    else:
                        j+=1
            i+=1
        return self.clean()
    def removeVariablesPOS(self,vars):  #result is simplify() and simplifyPOS()
        for i in xrange(len(self.ops)):
            self.ops[i]=self.ops[i].removeVariablesPOS(vars).clean()
        return self.clean().simplifyPOS()
    def evaluate(self,val):             #result is simplify()
        for i in xrange(len(self.ops)):
            self.ops[i]=self.ops[i].evaluate(val)
        return self.clean()
    def satsolvePOS(self):				#simplify(), simplifyPOS() first
        found=True
        for o in self.ops:
            if not (isinstance(o,VarOp) or isinstance(o,NotOp) or isinstance(o,TrueOp)):
                assumption=o.ops[0]
                assumptionInv=assumption.invert()
                
                cp=self.copy()
                cp.ops.insert(0,assumption)
                cp=cp.simplifyPOS()
                res=cp.satsolvePOS()
                if res:
                    return res
                else:
                    cp=self.copy()
                    cp.ops.insert(0,assumptionInv)
                    cp=cp.simplifyPOS()
                    res=cp.satsolvePOS()
                    return res
        return self
    def size(self):
    	return len(self.ops)
    def copy(self):
        return AndOp([o.copy() for o in self.ops])
    def __str__(self):
        opsstrings = [str(o) for o in self.ops]
        return "("+".".join(opsstrings)+")"
        
class OrOp(Op):
    def __init__(self,ops):
        assert isinstance(ops,list)
        self.ops=ops
    def invert(self):
        return AndOp([NotOp(o) for o in self.ops])
    def reduceNotOps(self):
        return OrOp([o.reduceNotOps() for o in self.ops]).clean()
    def isValidPOS(self):
        for o in self.ops:
            if isinstance(o, AndOp):
                return False
            elif not o.isValidPOS():
                return False
        return True
    def isValidSOP(self):
        for o in self.ops:
            if not o.isValidSOP():
                return False
        return True
    def simplify(self):
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].simplify()
        return self.clean()
    def clean(self):
        varList=[]
        varInvertedList=[]
        i=0
        while i<len(self.ops):
            o=self.ops[i]
            if isinstance(o, OrOp):
                self.ops.extend(o.ops)
                self.ops.pop(i)
                i-=1
            elif isinstance(o, VarOp):
                if o in varList:
                    self.ops.pop(i)
                    i-=1
                elif o in varInvertedList:
                    return TrueOp()
                else:
                    varList.append(o)
            elif isinstance(o, TrueOp):
                return TrueOp()
            elif isinstance(o, NotOp):
                if isinstance(o.op, VarOp):
                    if o.op in varList:
                        return TrueOp()
                    elif o.op in varInvertedList:
                        self.ops.pop(i)
                        i-=1
                    else:
                        varInvertedList.append(o.op)
                elif isinstance(o.op, TrueOp) and len(self.ops)>1:
                    self.ops.pop(i)
                    i-=1
            i+=1
        if len(self.ops)==1:
            return self.ops[0]
        self.ops.sort(compareSize)
        return self
    def reduceToPOS(self):
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].reduceToPOS()
        while len(self.ops)>=2:
            o1=self.ops[-1]
            self.ops.pop(-1)
            if not isinstance(o1,AndOp):
                o1=AndOp([o1])
            o2=self.ops[-1]
            self.ops.pop(-1)
            if not isinstance(o2,AndOp):
                o2=AndOp([o2])
            orList=[OrOp([ob, oa]).clean() for oa in o1.ops for ob in o2.ops]
            res=AndOp(orList).clean().simplifyPOS()
            self.ops.append(res)
        return self.clean() #.simplifyPOS()
    def reduceToSOP(self):
        for i in xrange(len(self.ops)):
            self.ops[i] = self.ops[i].reduceToSOP()
        return self.clean().simplifySOP()
    def canonicalise(self):
        for o in self.ops:
            o.canonicalise()
        self.ops.sort(compareOp)
        return self
    def simplifySOP(self):  #simplify() first, result is simplify()
        i=0
        while i<len(self.ops):
            o1=self.ops[i]
            o1inv=o1.invert()
            j=i+1
            if isinstance(o1,VarOp) or isinstance(o1,NotOp):
                while j<len(self.ops):
                    o2=self.ops[j]
                    if isinstance(o2,VarOp) or isinstance(o2,NotOp):
                        j+=1
                    else:
                        if o1 in o2.ops:
                            self.ops.pop(j)
                        else:
                            if o1inv in o2.ops:
                                o2.ops.remove(o1inv)
                                o2=o2.clean()
                                self.ops.pop(j)
                                k=i+1
                                while k<len(self.ops):
                                    if compareSize(o2,self.ops[k])==-1:
                                        self.ops.insert(k,o2)
                                        break
                                    k+=1
                                if k==len(self.ops):
                                    self.ops.append(o2)
                            j+=1
            else:
                while j<len(self.ops):
                    if productImplies(o1,self.ops[j]):
                        self.ops.pop(j)
                    else:
                        j+=1
            i+=1
        return self.clean()
    def removeVariablesPOS(self,vars):
        ops=[]
        for o in self.ops:
            if isinstance(o,NotOp):
                if o.op not in vars:
                    ops.append(o)
            else:
                if o not in vars:
                    ops.append(o)
        self.ops=ops
        if len(self.ops)==0:
            return NotOp(TrueOp())
        return self
    def evaluate(self,val):
        for i in xrange(len(self.ops)):
            self.ops[i]=self.ops[i].evaluate(val)
        return self.clean()
    def size(self):
    	return len(self.ops)
    def copy(self):
        return OrOp([o.copy() for o in self.ops])
    def __str__(self):
        opsstrings = [str(o) for o in self.ops]
        return "("+"+".join(opsstrings)+")"
        
def falseOpCreate():
    return NotOp(TrueOp())

def equalsOpCreate(o1,o2):
    return OrOp([AndOp([o1,o2]), AndOp([NotOp(o1),NotOp(o2)])])
    
def xorOpCreate(o1,o2):
    return OrOp([AndOp([o1,NotOp(o2)]), AndOp([NotOp(o1),o2])])

def impliesOpCreate(o1,o2):
    return OrOp([NotOp(o1), o2])

def iteOpCreate(i,t,e):
    return OrOp([AndOp([i,t]),AndOp([NotOp(i),e])])

def truthTableOpCreate(vars,vals):
    assert 2**len(vars)==len(vals)
    orList=[]
    for i in xrange(2**len(vars)):
        andList=[]
        for j in xrange(len(vars)):
            if i&(1<<(len(vars)-j-1))!=0:
                andList.append(NotOp(vars[j]))
            else:
                andList.append(vars[j])
        andList.append(vals[i])
        orList.append(AndOp(andList))
    return OrOp(orList)


def main():
    a=VarOp("a")
    b=VarOp("b")
    c=VarOp("c")
    d=VarOp("d")
    
    xa=VarOp("xa")
    xb=VarOp("xb")
    xc=VarOp("xc")
    xd=VarOp("xd")
    x0=VarOp("x0")
    x1=VarOp("x1")
    x2=VarOp("x2")
    x3=VarOp("x3")
    x4=VarOp("x4")
    x5=VarOp("x5")
    x6=VarOp("x6")
    x7=VarOp("x7")
    x8=VarOp("x8")
    x9=VarOp("x9")
    x10=VarOp("x10")
    x11=VarOp("x11")
    x12=VarOp("x12")
    x13=VarOp("x13")
    x14=VarOp("x14")
    x15=VarOp("x15")
    v0=VarOp("v0")
    v1=VarOp("v1")
    v2=VarOp("v2")
    v3=VarOp("v3")
    v4=VarOp("v4")
    v5=VarOp("v5")
    v6=VarOp("v6")
    v7=VarOp("v7")
    v8=VarOp("v8")
    v9=VarOp("v9")
    v10=VarOp("v10")
    v11=VarOp("v11")
    v12=VarOp("v12")
    v13=VarOp("v13")
    v14=VarOp("v14")
    v15=VarOp("v15")
    
    def testRun(name, f):
        print name
        f=f.canonicalise()
        print f
        f=f.reduceNotOps()
        print f
        f=f.reduceToPOS().simplifyPOS().canonicalise()
        print f
        if f.isValidPOS():
            print "valid POS"
        f=f.reduceToSOP().simplifySOP().canonicalise()
        print f
        if f.isValidSOP():
            print "valid SOP"
    
    f=OrOp([a,NotOp(b),c,NotOp(TrueOp()),NotOp(TrueOp()),OrOp([a,d])])
    testRun("f1",f)
    f=AndOp([a,NotOp(b),c,TrueOp(),TrueOp(),AndOp([a,d])])
    testRun("f2",f)
    g=NotOp(OrOp([AndOp([a,NotOp(b)]),c]))
    testRun("g",g)
    h=OrOp([AndOp([a,b]),AndOp([c,NotOp(b)])])
    testRun("h",h)
    
    
    f=AndOp([OrOp([a,x0]), OrOp([a.invert(), d,c]), OrOp([d.invert(), b, a.invert()]), OrOp([d.invert(), b.invert(), a.invert()])])
    f=f.reduceNotOps()
    f=f.reduceToPOS()
    f=f.simplifyPOS()
    print f
    
    sol=f.satsolvePOS()
    print str(sol)
    
    
    f=AndOp([OrOp([a,x0]), OrOp([x1,x0]), OrOp([a.invert(), d,c]), OrOp([d.invert(), b, x1.invert()]), OrOp([d.invert(), b.invert(), x1.invert()]), OrOp([d,x1.invert(),a.invert(),c.invert()])])
    f=f.reduceNotOps()
    f=f.reduceToPOS()
    f=f.simplifyPOS()
    print f
    
    sol=f.satsolvePOS()
    print sol
    #exit()
    
    
    F=OrOp([AndOp([a,b,x0]),AndOp([a,NotOp(b),x1])])
    testRun("F1",F)
    
    F=OrOp([AndOp([a,b,x0]),AndOp([a,NotOp(b),x1]),AndOp([NotOp(a),b,x2]),AndOp([NotOp(a),NotOp(b),x3])])
    #testRun("F1",F)
    print "F2"
    F=F.canonicalise()
    F=F.reduceNotOps()
    print F
    G=F.copy()
    F=F.reduceToPOS()
    print F
    if F.isValidPOS():
        print "valid POS"
    G=G.reduceToSOP()
    print G
    if G.isValidSOP():
        print "valid SOP"
        
        
    F=OrOp([AndOp([a,b,c,x0]),
            AndOp([a,b,NotOp(c),x1]),
            AndOp([a,NotOp(b),c,x2]),
            AndOp([a,NotOp(b),NotOp(c),x3]),
            AndOp([NotOp(a),b,c,x4]),
            AndOp([NotOp(a),b,NotOp(c),x5]),
            AndOp([NotOp(a),NotOp(b),c,x6]),
            AndOp([NotOp(a),NotOp(b),NotOp(c),x7])])
    #testRun("F1",F)
    print "F3"
    F=F.canonicalise()
    F=F.reduceNotOps()
    print F
    G=F.copy()
    F=F.reduceToPOS()
    print F
    if F.isValidPOS():
        print "valid POS"
    G=G.reduceToSOP()
    print G
    if G.isValidSOP():
        print "valid SOP"
    
    G=AndOp([a, OrOp([a,b]), OrOp([NotOp(a),c]), OrOp([a,b,c]),OrOp([b,d,x0])])
    print G
    G=G.simplifyPOS()
    print G

    
if __name__=='__main__':
    main()