import Class.Route.phpMyAdmin as phpMyAdmin

def get(id=None):
    # sqlTest = "SELECT tests.id as testId,tests.time as testTime,tests.id_action as actionId,\
    #         actions.name as actionName,actions.brief as actionBrief,actions.chargeBool as actionChargeBool,\
    #         actions.crate_bool as actionCrateBool,actions.function as actionFunction,tests.comment as testComment,\
    #         tests.c_rate as testCrate,tests.running_bool as testRunningBool,cells.id as cellId,cells.name as cellName,\
    #         cells.soc as cellSoc, observers.id as observerId,observers.name as observerName, observers.function as observerFunction FROM `tests`\
    #         JOIN observers_relations ON tests.id = observers_relations.id_test\
    #         JOIN observers ON observers_relations.id_observer = observers.id\
    #         JOIN actions ON tests.id_action = actions.id\
    #         JOIN cells_relations ON cells_relations.id_test = tests.id\
    #         JOIN cells ON cells_relations.id_cell = cells.id"

    sqlCell = "SELECT cells.id, cells.name, cells.soc FROM cells JOIN cells_relations ON cells.id = cells_relations.id_cell WHERE cells_relations.id_test = "
    sqlObserver = "SELECT observers.id, observers.name, observers.function FROM observers\
          JOIN observers_relations ON observers.id = observers_relations.id_observer WHERE observers_relations.id_test = "
    sqlTest = "SELECT tests.id, tests.time, tests.id_action, actions.name, actions.brief, actions.chargeBool, actions.crate_bool,\
          actions.function, tests.comment, tests.c_rate, tests.running_bool FROM tests JOIN actions ON tests.id_action = actions.id"
    tab = []
    if (id != None):
        tab=phpMyAdmin.request(sqlTest + " WHERE tests.id = "+str(id), None)
        tab[0] = tab[0] + (phpMyAdmin.request(sqlCell+str(id), None),)
        tab[0] = tab[0] + (phpMyAdmin.request(sqlObserver+str(id),None),)
        return tab
    
    tab=phpMyAdmin.request(sqlTest, None)
    tab2 = []
    for elt in tab:
        elt= elt + (phpMyAdmin.request(sqlCell+str(elt[0]), None),)
        elt= elt + (phpMyAdmin.request(sqlObserver+str(elt[0]), None),)
        tab2.append(elt)
    return tab2

def put(test):
    if (test == None):
        return False
    test.id=phpMyAdmin.requestInsert("INSERT INTO tests (id_action, comment,c_rate,running_bool) VALUES ( %s, %s, %s, %s)\
                                 ", ( test.action.id, test.comment, test.c_rate, test.running_bool))
    # insert into the cells_relations table
    for cell in test.cellsList:
        phpMyAdmin.request("INSERT INTO cells_relations (id_test, id_cell) VALUES (%s, %s)", (test.id, cell.id))
    for observer in test.observersList:
        phpMyAdmin.request("INSERT INTO observers_relations (id_test, id_observer) VALUES (%s, %s)", (test.id, observer.id))
    # get the last inserted id
    return test.id

def delete(id):
    if (id == None):
        return False
    # delete from the cells_relations table
    phpMyAdmin.request("DELETE FROM cells_relations WHERE id_test = %s", (id,))
    # delete from the observer table
    phpMyAdmin.request("DELETE FROM observers_relations WHERE id_test = %s", (id,))
    # delete from the measures soh
    phpMyAdmin.request("DELETE FROM measures_soh WHERE id_test = %s", (id,))
    # delete from the measures observer table
    phpMyAdmin.request("DELETE o FROM measures_observers o INNER JOIN measures m ON m.id=o.id_measure WHERE m.id_test = %s", (id,))
    # delete from the measures table
    phpMyAdmin.request("DELETE FROM measures WHERE id_test = %s", (id,))
    # delete from the tests_relations table
    phpMyAdmin.request("DELETE FROM tests_relations WHERE id_test = %s", (id,))
    return phpMyAdmin.request("DELETE FROM tests WHERE id = %s", (id,))


def post(id,value):
    if(id == None):
        return False
    phpMyAdmin.request("UPDATE tests SET running_bool = %s WHERE id = %s",(value,id,))
    return