import Class.Route.phpMyAdmin as phpMyAdmin

def get(id=None):
    if (id != None):
        return phpMyAdmin.request("SELECT * FROM `cells` WHERE id = " + str(id[0]), None)
    return phpMyAdmin.request("SELECT * FROM `cells`", None)

def post(cell):
    return phpMyAdmin.request("INSERT INTO `cells` (`name`, `soc`) VALUES (%s, %s)", (cell.name,cell.soc,))

def update(cell):
    return phpMyAdmin.request("UPDATE `cells` SET name = %s, soc = %s WHERE id = %s", (cell.name,cell.soc,cell.id,))