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





def favourite():
    query = "SELECT med_name,med_brandname,med_purpose,med_price,medicine.med_role,dosage_form,medicine.med_id,med_quantity\
             FROM medicine\
             INNER JOIN favourite ON medicine.med_id = favourite.med_id and medicine.med_role = favourite.med_role\
             WHERE buyer_user = %s"
    connection = connect()
    cur = connection.cursor()
    try:
        params = (session['user'], )
        cur.execute(query, params)
        buid=buyid()
        items = cur.fetchall()
        ite, subtotal, items_len = cart_items()

    except mysql.connector.Error as err:
        print(err)
        return []
    finally:
        cur.close()
        connection.close()
    return render_template("favourite.html", items=items, subtotal=subtotal, items_len=items_len, buid=buid)




def fav():
    mid = request.form.get('med_id', None)
    r = request.form.get('med_role', None)
    buyer_user = session['user']
    query = "INSERT into favourite \
             (med_id,med_role,buyer_user)\
             VALUES (%s, %s, %s)"
    connection = connect()
    cur = connection.cursor()
    try:
        params = (mid, r, str(buyer_user), )
        cur.execute(query, params)
        flash("Препарт добавлен в избранное!!","success")
        connection.commit()
    except mysql.connector.Error as err:
        print(err)
    finally:
        cur.close()
        connection.close()
    return redirect(url_for('favourites'))