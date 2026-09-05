from .component import CircuitComponent
class Circuit:
 def __init__(self,nodes=()):self.nodes=set(nodes);self.components=[]
 def add(self,c):self.components.append(c)
