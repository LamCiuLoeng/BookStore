# -*- coding: utf-8 -*-
import traceback
from sys2do.model import *


#===============================================================================
# init the DB
#===============================================================================

def setup_db():
    try:
        metadata.create_all(engine)

        admin = User(user_name = "admin", email_address = "lamciuloeng@gmail.ocm", password = "admin")
        gadmin = Group(group_name = "admin")
        gadmin.users.append(admin)

        guser = Group(group_name = "user")

        DBSession.add_all([admin, gadmin, guser])
        DBSession.commit()
    except:
        traceback.print_exc()
        DBSession.rollback()


if __name__ == "__main__":
    setup_db()
    print "OK"
