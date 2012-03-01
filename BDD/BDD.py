#!/usr/bin/env python

import pygraphviz as pgv
import random

class Node:
    def isConstNode(self):
        return isinstance(self,ConstNode)

class ConstNode(Node):
    def __init__(self,v,inv=False):
        self.v=v
        self.var=None
        self.inv=inv
    
class IteNode(Node):
    def __init__(self,var,T,E,inv=False):
        self.var=var
        self.T=T
        self.E=E
        self.inv=inv
    def copy(self):
        return IteNode(self.var,self.T,self.E,self.inv)
    def __hash__(self):
        return hash(self.var)+hash(self.T)+hash(self.E)+hash(self.inv)
    def __eq__(self,other):
        return self.var==other.var and self.T==other.T and self.E==other.E and self.inv==other.inv
        
class UniqueTable:
    def __init__(self,varorder):
        self.table={}
        self.trueNode=ConstNode(1)
        self.falseNode=ConstNode(1,True)
        self.table[self.trueNode]=self.trueNode
        self.table[self.falseNode]=self.falseNode
        self.varorder=varorder
    def getNode(self,node):
        if node.T==node.E:
            return node.T
        res=self.table.get(node)
        if res:
            return res
        self.table[node]=node
        return node
    def getInvertedNode(self,node):
        if node==self.getTrueNode():
            return self.getFalseNode()
        elif node==self.getFalseNode():
            return self.getTrueNode()
        node=node.copy()
        node.inv=not node.inv
        res=self.table.get(node)
        if res:
            return res
        self.table[node]=node
        return node
    def getTrueNode(self):
        return self.trueNode
    def getFalseNode(self):
        return self.falseNode
        
    def recBDD(self,f,g,fn,depth):
        res=fn(self,f,g)
        if res:
            return res
        var=self.varorder[depth]
        if f.var!=var and g.var!=var:
            return self.recBDD(f,g,fn,depth+1)
        (f1,f2)=self.splitTop(f,var)
        (g1,g2)=self.splitTop(g,var)
        h1=self.recBDD(f1,g1,fn,depth+1)
        h2=self.recBDD(f2,g2,fn,depth+1)
        inv=False
        if h1.inv:
            h1=self.getInvertedNode(h1)
            h2=self.getInvertedNode(h2)
            inv=True
        return self.getNode(IteNode(var,h1,h2,inv))

    def splitTop(self,f,var):
        if f.var==var:
            t=f.T
            e=f.E
            if f.inv:
                t=self.getInvertedNode(t)
                e=self.getInvertedNode(e)
            return (t,e)
        else:
            return (f,f)
    
    def andFn(self,f,g):
        if f==self.getFalseNode():
            return self.getFalseNode()
        if g==self.getFalseNode():
            return self.getFalseNode()
        if f==self.getTrueNode() and g==self.getTrueNode():
            return self.getTrueNode()
        return None
        
    def orFn(self,f,g):
        if f==self.getTrueNode():
            return self.getTrueNode()
        if g==self.getTrueNode():
            return self.getTrueNode()
        if f==self.getFalseNode() and g==self.getFalseNode():
            return self.getFalseNode()
        return None
    
    def xorFn(self,f,g):
        if f.isConstNode() and g.isConstNode():
            if f==g:
                return self.getFalseNode()
            else:
                return self.getTrueNode()
        return None
    
        
    def andBDD(self,f,g):
        return self.recBDD(f,g,UniqueTable.andFn,0)
        
    def orBDD(self,f,g):
        return self.recBDD(f,g,UniqueTable.orFn,0)
                    
    def xorBDD(self,f,g,depth=0):
        return self.recBDD(f,g,UniqueTable.xorFn,0)
    
    def iteBDD(self,i,t,e):
        return self.orBDD(self.andBDD(i,t),self.andBDD(self.notBDD(i),e))
        
    def notBDD(self,f):
        if f==self.getTrueNode():
            return self.getFalseNode()
        elif f==self.getFalseNode():
            return self.getTrueNode()
        return self.getInvertedNode(f)
        
    def variableBDD(self,var):
        return self.getNode(
            IteNode(var,
                self.getTrueNode(),
                self.getFalseNode()))

def drawGraph(f,name,unique):
    def getNode(node,cache,G,cache2):
        if node==unique.getTrueNode():
            return ("1",False)
        elif node==unique.getFalseNode():
            return ("1",False)
        nnode=IteNode(node.var,node.T,node.E,False)
        res=cache.get(nnode)
        if res:
            return (res,False)
        new=str(node.var)+"_"+str(random.randrange(10,100))
        cache[nnode]=new
        #G.add_node(new)
        c2=cache2.get(nnode.var)
        if c2:
            c2.append(new)
        else:
            cache2[nnode.var]=[new]
        return (new,True)
    def drawGraphRec(node,cache,G,cache2):
        (this,garbage)=getNode(node,cache,G,cache2)
        (T,tnew)=getNode(node.T,cache,G,cache2)
        (E,enew)=getNode(node.E,cache,G,cache2)
        if node.T.inv:
            G.add_edge(this,T,color="red")
        else:
            G.add_edge(this,T)
        if node.E.inv:
            G.add_edge(this,E,style="dotted",color="green")
        else:
            G.add_edge(this,E,style="dashed")
        if tnew:
            drawGraphRec(node.T,cache,G,cache2)
        if enew:
            drawGraphRec(node.E,cache,G,cache2)
    
    G=pgv.AGraph(ranksep='0.3',nodesep="0.3",strict=False)
    cache={}
    cache2={}
    G.add_node("1")
    G.add_node("F")
    (n,new)=getNode(f,cache,G,cache2)
    if f.inv:
        G.add_edge("F",n,style="dotted",color="green")
    else:
        G.add_edge("F",n)
    if new:
        drawGraphRec(f,cache,G,cache2)
    
    for i,v in cache2.iteritems():
        print v
        B=G.add_subgraph(v,rank='same')

    #print G.string()
    G.layout(prog='dot')
    G.draw(name+'.pdf')


def main():
    a="a"
    b="b"
    c="c"
    d="d"
    e="e"
    x0="x0"
    x1="x1"
    
    unique=UniqueTable([a,x0,d,b,c,e,x1])
    
    f1=unique.variableBDD(a)
    f2=unique.variableBDD(b)
    f3=unique.variableBDD(c)
    fd=unique.variableBDD(d)
    fx0=unique.variableBDD(x0)
    fx1=unique.variableBDD(x1)
    
    #f4=unique.andBDD(f1,f2)
    #f4=unique.notBDD(f4)
    #f4=unique.notBDD(f2)
    f4=unique.andBDD(f1,unique.notBDD(f2))
    #f4=unique.notBDD(f2)
    #f4=unique.andBDD(f4,f3)
    
    #f4=orBDD(f3,variableBDD(c,unique),unique)
    #f4=unique.orBDD(
        #unique.andBDD(f3,unique.notBDD(f4)),
        #unique.andBDD(f4,unique.notBDD(f3)))
    
    f5=unique.getNode(IteNode(b,f3,unique.getFalseNode()))
    f4=unique.getNode(IteNode(a,f3,f5))
    
    #f4=unique.xorBDD(f4,unique.variableBDD(d))
    
    #f4=unique.iteBDD(unique.variableBDD(d),f4,unique.variableBDD(e))
    #f4=unique.iteBDD(f4,unique.variableBDD(d),unique.variableBDD(e))
    
    f5=unique.xorBDD(fx0,fx1)
    f4=unique.iteBDD(fd,f4,f5)
    
    
    drawGraph(f4,"test",unique)
    
if __name__=='__main__':
    main()
    