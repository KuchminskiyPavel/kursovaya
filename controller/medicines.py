
import mysql.connector
from flask import session
from flask import redirect, url_for, render_template
from controller.cart import cart_items
from controller.utilities import buyid
from controller.utilities import connect





def product_detail(pur):
    query = "SELECT med_name,med_brandname,med_purpose,med_price,med_role,dosage_form,med_id\
             FROM medicine\
             WHERE med_purpose = %s"
    try:
        connection = connect()
        cur = connection.cursor()
        params = (pur, )
        cur.execute(query, params)
        items = cur.fetchall()
        ite, subtotal, items_len = cart_items()
        buid=buyid()
    except mysql.connector.Error as err:
        print(err)
        return []
    finally:
        cur.close()
        connection.close()
    return render_template("product.html", items=items, subtotal=subtotal, items_len=items_len, buid=buid)