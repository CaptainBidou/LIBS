import Class.Route.phpMyAdmin as phpMyAdmin

def get(id=None):
    if (id != None):
        return phpMyAdmin.request("SELECT * FROM `actions` WHERE id = " + str(id[0]), None)
    return phpMyAdmin.request("SELECT * FROM `actions`", None)