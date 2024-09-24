import Class.Route.phpMyAdmin as phpMyAdmin
# "SELECT output_voltage,current,ambient_temperature,surface_temperature_plus,surface_temperature_minus FROM measures WHERE id_test = %s ORDER BY ID ASC", (idTest,)
def get(param):
    tab=phpMyAdmin.request("SELECT id,output_voltage,current,ambient_temperature,surface_temperature_plus,surface_temperature_minus FROM measures\
                            WHERE id_test = %s ORDER BY ID ASC", (param[0],))
    tab2 = []
    for a in tab:
        observersVal=phpMyAdmin.request("SELECT soc,observers.function FROM measures_observers JOIN observers ON observers.id = measures_observers.id_observer\
                                        WHERE id_measure = %s ORDER BY id_observer ASC", (a[0],))
        a = a + (observersVal,)
        tab2.append(a)
    return tab2