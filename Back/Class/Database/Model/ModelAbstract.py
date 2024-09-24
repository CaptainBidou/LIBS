###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
from abc import ABC, abstractmethod
###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################
class Model():
    @abstractmethod
    def __init__(self):
        self.Qn = 3.08
        self.SAMPLING_RATE = 1
        raise NotImplementedError
    
    @abstractmethod
    def runOneStep(self,z,u,charge):
        raise NotImplementedError

    @abstractmethod
    def toString():
        raise NotImplementedError