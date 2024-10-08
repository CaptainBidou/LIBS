import Class.Route.phpMyAdmin as phpMyAdmin
# import phpMyAdmin

def get(idCell):
    if idCell == None:
        return phpMyAdmin.request("SELECT id_cell,cells.name,cells.soc, AVG(r0), MAX(r0), MIN(r0) FROM cells JOIN measures_soh ON cells.id=measures_soh.id_cell GROUP BY cells.id", None)
    return phpMyAdmin.request("SELECT id_cell,cells.name,cells.soc, AVG(r0), MAX(r0), MIN(r0) FROM cells JOIN measures_soh ON cells.id=measures_soh.id_cell WHERE id_cell = %s GROUP BY cells.id", (idCell[0],))

def put(measure_soh):
    return phpMyAdmin.request("INSERT INTO `measures_soh` (`id_cell`,`id_test`,`time`,`voc`,`ia`,`vb`,`ib`,`r0`,`soc`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (measure_soh.cell.id,measure_soh.test.id,measure_soh.time,measure_soh.voc,measure_soh.ia,
                                                                                                                                                                      measure_soh.vb,measure_soh.ib,measure_soh.r0,measure_soh.soc))