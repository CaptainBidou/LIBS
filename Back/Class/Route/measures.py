import Class.Route.phpMyAdmin as phpMyAdmin

def get(data):
    if (data.__len__() == 2):
        return phpMyAdmin.request("SELECT * FROM `measures` WHERE id_test = " + str(data[0]) + " AND id > " + str(data[1]), None)
    return phpMyAdmin.request("SELECT * FROM `measures` WHERE id_test = " + str(data[0]), None)

def put(measure):
    return phpMyAdmin.requestInsert("INSERT INTO `measures` (`id_test`,`id_cell`,`current`,`output_voltage`,`ambient_temperature`,`surface_temperature_plus`\
                              ,`surface_temperature_minus`) VALUES (%s, %s, %s, %s, %s, %s, %s)", measure.toTuple())
