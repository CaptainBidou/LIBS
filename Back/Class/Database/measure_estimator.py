import Class.Database.measure
import Class.Database.observer
import json

class measure_estimator():
    def __init__(self,tuple):
        
        self.measure = Class.Database.measure.measure((tuple[0],tuple[1],tuple[2],tuple[3],tuple[4],tuple[5],tuple[6],tuple[7],tuple[8],tuple[9],tuple[10],tuple[11]))
        
        self.tabEstimator = []

        for elt in tuple[12]:
            mobs={}
            mobs['id'] = elt[0]
            mobs['id_measure'] = elt[1]
            mobs['observer'] = Class.Database.observer.observer((elt[7],elt[8],elt[9],))
            mobs['surface_temperature'] = elt[3]
            mobs['core_temperature'] = elt[4]
            mobs['output_voltage'] = elt[5]
            mobs['soc'] = elt[6]
            self.tabEstimator.append(mobs)


    def toString(self):
        stri = '{"measure":' + self.measure.toString() + ',"estimation":'
        for elt in self.tabEstimator:
            stri += '{"id":"'+str(elt['id'])+'","observer":'+elt['observer'].toString()+',"surface_temperature":"'+str(elt['surface_temperature'])\
            +'","output_voltage":"'+str(elt['output_voltage'])+'","soc":"'+str(elt['soc'])+'","core_temperature":"'+str(elt["core_temperature"])+'"}'
        stri += '}'
        return stri



class measure_estimatorConstruct():
    def __init__(self,measureid,observerid,surface_temperature,core_temperature,output_voltage,soc):
        self.measureid = measureid
        self.id_observer = observerid
        self.surface_temperature = surface_temperature
        self.core_temperature = core_temperature
        self.output_voltage = output_voltage
        self.soc = soc
    def commit(self):
        #TODO
        pass