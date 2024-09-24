import Class.Route.phpMyAdmin as phpMyAdmin

def get(data):
    # 0 id test
    # 1 last id 
    # 2 estimator
    # 3 cellule
    if data.__len__() == 1:
        tab = phpMyAdmin.request("SELECT * FROM measures JOIN cells ON measures.id_cell = cells.id WHERE id_test = %s AND measures.id_cell = %s  ORDER BY measures.id ASC", (data[0],data[3],))
    else:
        tab = phpMyAdmin.request("SELECT * FROM measures JOIN cells ON measures.id_cell = cells.id WHERE id_test = %s AND measures.id > %s AND measures.id_cell = %s ORDER BY measures.id ASC", (data[0],data[1],data[3],))
    tab2 = []
    for a in tab:
        elt = phpMyAdmin.request("SELECT * FROM measures_observers JOIN observers ON observers.id = measures_observers.id_observer WHERE id_measure = %s AND id_observer = %s", (a[0],data[2],))
        a = a + (elt,) 
        tab2.append(a)
    return tab2  


def put(measure):
    return phpMyAdmin.requestInsert("INSERT INTO measures_observers (id_measure,id_observer,surface_temperature,core_temperature,output_voltage,soc) VALUES\
                                     (%s,%s,%s,%s,%s,%s)",(measure.measureid,measure.id_observer,measure.surface_temperature,measure.core_temperature,\
                                                            measure.output_voltage,measure.soc))
