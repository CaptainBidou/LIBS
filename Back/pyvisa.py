###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################

###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def ResourceManager():
    return resMan()
###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################
class resMan():
    def __init__(self):
        pass
    def list_resources(self):
        pass
    def open_resource(self,resID):
        print(resID)
        return devMan()


class devMan():
    def __init__(self):
        pass
    def query(self,command):
        print(command)
        if(command == "*IDN?"):
            return "Fake Device"
        if(command =="MEASure:VOLTage?"):
            return 3.50
        if(command =="MEASure:CURRent?"):
            return 1.50
        pass
    def write(self,command):
        print(command)
        pass
