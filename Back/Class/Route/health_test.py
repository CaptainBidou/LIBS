import Class.Route.phpMyAdmin as phpMyAdmin

def get(data):
    sqlHealth = "SELECT * FROM health_tests WHERE id = "+data[0]
    sqlCell = "SELECT cells.id, cells.name, cells.soc FROM cells JOIN cells_relations ON cells.id = cells_relations.id_cell WHERE cells_relations.id_test = "
    sqlObserver = "SELECT observers.id, observers.name, observers.function FROM observers\
        JOIN observers_relations ON observers.id = observers_relations.id_observer WHERE observers_relations.id_test = "
    sqlTest = "SELECT tests.id, tests.time, tests.id_action, actions.name, actions.brief, actions.chargeBool, actions.crate_bool,\
        actions.function, tests.comment, tests.c_rate, tests.running_bool FROM tests JOIN actions ON tests.id_action = actions.id\
            JOIN tests_relations ON tests.id = tests_relations.id_test WHERE tests_relations.id_health_test = "+data[0]
    sqlTime = "SELECT time_resting FROM tests_relations WHERE id_health_test = "+data[0]+" ORDER BY id_test ASC"
    timeTab = phpMyAdmin.request(sqlTime, None)

    tab=phpMyAdmin.request(sqlTest, None)
    tab2 = []
    for elt in tab:
        elt= elt + (phpMyAdmin.request(sqlCell+str(elt[0]), None),)
        elt= elt + (phpMyAdmin.request(sqlObserver+str(elt[0]), None),)
        tab2.append(elt)

    tab = phpMyAdmin.request(sqlHealth, None)
    tab[0] = tab[0] + (tab2,)+(timeTab,)
    return tab

def delete(data):
    if (id == None):
        return False
    
    tabId = phpMyAdmin.request("SELECT test_id from tests_relations WHERE id_health_test = %s",(data[0],))
    # for id in tabId :
    # # delete from the cells_relations table
    # phpMyAdmin.request("DELETE FROM cells_relations WHERE id_test = %s", (id,))
    # # delete from the observer table
    # phpMyAdmin.request("DELETE FROM observers_relations WHERE id_test = %s", (id,))
    # # delete from the measures soh
    # phpMyAdmin.request("DELETE FROM measures_soh WHERE id_test = %s", (id,))
    # # delete from the measures observer table
    # phpMyAdmin.request("DELETE o FROM measures_observers o INNER JOIN measures m ON m.id=o.id_measure WHERE m.id_test = %s", (id,))
    # # delete from the measures table
    # phpMyAdmin.request("DELETE FROM measures WHERE id_test = %s", (id,))

    # return phpMyAdmin.request("DELETE FROM tests WHERE id = %s", (id,))