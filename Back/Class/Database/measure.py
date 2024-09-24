import Class.Database.cell
class measure():
    def __init__(self,tuple):
        self.id = tuple[0]
        self.id_test = tuple[2]
        self.time = tuple[3]
        self.current = tuple[4]
        self.output_voltage = tuple[5]
        self.ambient_temperature = tuple[6]
        self.surface_temperature_plus = tuple[7]
        self.surface_temperature_minus = tuple[8]
        self.cell = Class.Database.cell.cell((tuple[9],tuple[10],tuple[11],))
    def toString(self):
        return '{"id":"' + str(self.id)+ '","cell":' + self.cell.toString() + ',"id_test":"' + str(self.id_test) + '","time":"' + str(self.time) +\
        '","current":"' + str(self.current) + '","output_voltage":"' + str(self.output_voltage) +\
        '","ambient_temperature":"' + str(self.ambient_temperature) + '","surface_temperature_plus":"' +\
         str(self.surface_temperature_plus) + '","surface_temperature_minus":"' + str(self.surface_temperature_minus) + '"}'

class measureConstruct():
    def __init__(self,test,cell,current,output_voltage,ambient_temperature,surface_temperature_plus,surface_temperature_minus):
        self.test = test
        self.cell=cell
        self.current = current
        self.output_voltage = output_voltage
        self.ambient_temperature = ambient_temperature
        self.surface_temperature_plus = surface_temperature_plus
        self.surface_temperature_minus = surface_temperature_minus
    def toTuple(self):
        # `id_test`,`time`,`current`,`output_voltage`,`ambient_temperature`,`surface_temperature_plus`\
        #                       ,`surface_temperature_minus`
        return (self.test.id,self.cell.id,self.current,self.output_voltage,self.ambient_temperature,self.surface_temperature_plus,self.surface_temperature_minus)