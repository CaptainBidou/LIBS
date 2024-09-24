class export():
    # [(1, 5.0, 2.01, 21.0, 22.0, 20.0, [(1.0, 'Observer'), (0.9999, 'FNN')])]
    def __init__(self,tuple):
        self.blob = "time;voltage;current;ambient_temperature;surface_temperature_plus;surface_temperature_minus"
        for a in tuple[0][6]:
            self.blob += ";"+a[1]
        self.blob += "\n"
        time =0
        for a in tuple:
            self.blob += str(time)+";"+str(float(a[1]))+";"+str(float(a[2]))+";"+str(float(a[3]))+";"+str(float(a[4]))+";"+str(float(a[5]))
            for b in a[6]:
                self.blob += ";"+str(float(b[0]))
            self.blob += "\n"
            time = time +1
    def toString(self):
        return self.blob