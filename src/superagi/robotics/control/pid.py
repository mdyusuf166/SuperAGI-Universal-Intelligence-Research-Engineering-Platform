class PIDController:
 def __init__(self,kp=1,ki=0,kd=0):self.kp,self.ki,self.kd=kp,ki,kd;self.integral=0;self.previous=0
 def compute(self,target,current,dt=1):
  error=target-current;self.integral+=error*dt;out=self.kp*error+self.ki*self.integral+self.kd*(error-self.previous)/dt;self.previous=error;return {"value":out,"classification":"SIMULATION CONTROL"}
