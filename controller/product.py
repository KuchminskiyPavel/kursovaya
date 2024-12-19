# from flask_mysqldb import MySQL
import mysql.connector
from flask import session
from controller.cart import cart_items
from flask import redirect, url_for, render_template
from flask import flash
from flask import request
# import MySQLdb
from controller.utilities import buyid
from controller.utilities import connect




def single_product(pid, rol):
    query = "SELECT med_name,med_brandname,med_purpose,med_price,med_role,dosage_form,med_quantity,med_id,med_expiry\
             FROM medicine\
             WHERE med_id= %s and med_role = %s"
    connection = connect()
    cur = connection.cursor()
    try:
        params = (str(pid), str(rol), )
        cur.execute(query, params)
        items = cur.fetchone()
        ite, subtotal, items_len = cart_items()
        buid = buyid()

        query = "SELECT med_name,med_brandname,med_purpose,med_price,med_role,med_id\
                 FROM medicine\
                 WHERE med_purpose = %s and med_role = %s LIMIT 3"
        param = (str(items[2]), str(items[4]), )
        cur.execute(query, param)
        rel = cur.fetchall()
    except mysql.connector.Error as err:
        print(err)
        return []
    finally:
        cur.close()
        connection.close()
    return render_template("single-product.html", items=items, subtotal=subtotal, items_len=items_len, rel=rel, buid=buid)