from flask_bcrypt import Bcrypt
from flask import request, session
from flask import flash
from flask_mysqldb import MySQL
import mysql.connector
from flask import Flask
from flask import redirect, url_for, render_template
import pandas as pd
import openpyxl
from flask import send_file

from controller.utilities import category_items, cart_value, upass, buyid, connect
from controller.order import orhistory
from controller.cart import add_item, cart_items, delete_item, update_item
from controller.medicines import product_detail
from controller.product import single_product
from controller.search import query_search
from controller.favourites import fav, favourite
from controller.checkout import normal_checkout, checkout_details
from controller.supplier import ssearch, supproduct_detail
from controller.supplier_main import supadd, supupdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from functools import wraps


app = Flask(__name__)
app.secret_key = "super secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = '3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'parol'
app.config['MYSQL_DB'] = 'ph'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def send_email(sender, recipient, subject, message):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'karlson7788@gmail.com'
    smtp_password = 'vsab rslr awvb oaeg'

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        else:
            flash("Сначала требуется регистрация!!", category="danger")
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session and session['type'] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("Необходимо войти как администратор!!", category="danger")
            return redirect(url_for('login'))
    return wrap

def customer_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session:
            if session['type'] == 'customer' or session['type'] == 'supplier':
                return f(*args, **kwargs)
            else:
                flash("Сначала требуется зарегистрироваться как покупатель!!", category="danger")
                return redirect(url_for('login'))
        else:
            flash("Сначала нужно зарегистрироваться!!", category="danger")
            return redirect(url_for('login'))
    return wrap

def supplier_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session and session['type'] == 'supplier':
            return f(*args, **kwargs)
        else:
            flash("Сначала требуется зарегистрироваться как поставщик!!", category="danger")
            return redirect(url_for('login'))
    return wrap

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Вы успешно вышли!!", category="success")
    return redirect(url_for('home'))

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        query = "SELECT * FROM login WHERE user_email = %s"

        connection = connect()
        cur = connection.cursor()
        try:
            cur.execute(query, (email,))
            user = cur.fetchone()
            if user:
                if bcrypt.check_password_hash(user[2], password):
                    session['email'] = email
                    session['user'] = user[0]
                    session['type'] = user[6]
                    session['person'] = user[3]
                    session['cdis'] = 0.00
                    session['pdis'] = 0.00

                    if user[6] == "admin":
                        session['person'] = user[3]
                        flash("Выполнен вход как администратор!!", 'success')
                        return redirect(url_for('admin_dashboard'))
                    elif user[6] == "supplier":
                        flash("Выполнен вход как поставщик!!", 'success')
                        return redirect(url_for('supplier'))
                    else:
                        flash("Выполнен вход как покупатель!!", 'success')
                        return redirect(url_for('mhome'))
                else:
                    flash("Неправильный пароль!!", 'danger')
                    return redirect(url_for('login'))
            else:
                flash("Email не существует!!", 'danger')
                return redirect(url_for('login'))
        except mysql.connector.Error as e:
            print(e)
            return None
        finally:
            cur.close()
            connection.close()
    return render_template("abc.html", title='Login')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        hashed_pass = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        address = request.form['address']
        category = request.form['category']
        connection = connect()
        cur = connection.cursor()
        cur.execute("SELECT * FROM login WHERE user_email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user is None:
            send_email('karlson7788@gmail.com', email, 'Регистрация', 'Регистрация прошла успешно ')
            cur.execute("INSERT INTO login(user_email, user_pass, user_first_name, user_last_name, user_address, user_category) VALUES(%s, %s, %s, %s, %s, %s)",
                        (email, hashed_pass, fname, lname, address, category))
            connection.commit()
            flash("Регистрация прошла успешно!!", 'success')
            return redirect(url_for('login'))
        else:
            flash("Email уже существует!!", 'danger')
            return redirect(url_for('signup'))

    return render_template("signup.html", title='SignUp')

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/users")
@admin_required
def admin_users():
    connection = connect()
    cur = connection.cursor()
    cur.execute("SELECT * FROM login")
    users = cur.fetchall()
    cur.close()
    return render_template("admin_users.html", users=users)

@app.route("/admin/orders")
@admin_required
def admin_orders():
    connection = connect()
    cur = connection.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()
    return render_template("admin_orders.html", orders=orders)

@app.route("/admin/medicines")
@admin_required
def admin_medicines():
    connection = connect()
    cur = connection.cursor()
    cur.execute("SELECT * FROM medicine")
    medicines = cur.fetchall()
    cur.close()
    return render_template("admin_medicines.html", medicines=medicines)

@app.route("/admin/delete_order/<int:order_id>", methods=['POST'])
@admin_required
def delete_order(order_id):
    connection = connect()
    cur = connection.cursor()
    try:
        cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        connection.commit()
        flash("Заказ успешно удален!", 'success')
    except mysql.connector.Error as e:
        flash("Ошибка при удалении заказа: {}".format(e), 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin_orders'))

@app.route("/admin/delete_medicine/<int:medicine_id>", methods=['POST'])
@admin_required
def delete_medicine(medicine_id):
    connection = connect()
    cur = connection.cursor()
    try:
        cur.execute("DELETE FROM medicine WHERE med_id = %s", (medicine_id,))
        connection.commit()
        flash("Препарат успешно удален!", 'success')
    except mysql.connector.Error as e:
        flash("Ошибка при удалении препарата: {}".format(e), 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin_medicines'))

@app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
@admin_required
def delete_user(user_id):
    connection = connect()
    cur = connection.cursor()
    try:
        cur.execute("DELETE FROM login WHERE user_id = %s", (user_id,))
        connection.commit()
        flash("Пользователь успешно удален!", 'success')
    except mysql.connector.Error as e:
        flash("Ошибка при удалении пользователя: {}".format(e), 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin_users'))

@app.route("/admin/medication_stats")
@admin_required
def medication_stats():
    connection = connect()
    cur = connection.cursor()

    cur.execute("SELECT med_id, med_name, med_quantity, med_price,med_expiry,added_at FROM medicine")
    medications = cur.fetchall()

    df = pd.DataFrame(medications, columns=['ID', 'Название', 'Количество', 'Цена','Срок годности', 'Дата добавления'])

    excel_file = "medication_stats.xlsx"
    df.to_excel(excel_file, index=False)

    cur.close()

    return send_file(excel_file, as_attachment=True)


@app.route("/admin/medicine_statistics")
@admin_required
def medicine_statistics():
    connection = connect()
    cur = connection.cursor()


    cur.execute("SELECT COUNT(*) FROM medicine")
    total_meds = cur.fetchone()[0]

    cur.execute("SELECT AVG(med_price) FROM medicine")
    avg_price = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM medicine WHERE med_quantity < 100")
    low_stock = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM medicine WHERE med_expiry <= CURDATE() + INTERVAL 30 DAY")
    expiring_soon = cur.fetchone()[0]


    cur.execute("""
        SELECT DATE(added_at) AS date, COUNT(*) AS count 
        FROM medicine 
        GROUP BY DATE(added_at) 
        ORDER BY DATE(added_at) DESC
    """)
    day_data = cur.fetchall()

    cur.execute("""
        SELECT HOUR(added_at) AS hour, COUNT(*) AS count 
        FROM medicine 
        GROUP BY HOUR(added_at) 
        ORDER BY HOUR(added_at) DESC
    """)
    hour_data = cur.fetchall()
    cur.close()

    return render_template(
        "admin_medicine_statistics.html",
        total_meds=total_meds,
        avg_price=avg_price,
        low_stock=low_stock,
        expiring_soon=expiring_soon,
        day_data=day_data,
        hour_data=hour_data,
    )




@app.route("/ccoupon", methods=['POST'])
@customer_required
def coupon():
    items, subtotal, items_len = cart_items()
    buid = buyid()
    couponcode = request.form.get('coupo', None)
    dis = 0.00
    val = 0
    if session['type'] == 'customer':
        if couponcode == 'sup':
            flash("!Скидка применена!", category="success")
            coupon = subtotal * 0.15
            session['cdis'] = coupon
            dis = coupon
            val = 1
        else:
            flash("Неверный код скидки", category="danger")
    return render_template(
        "cart.html",
        items=items,
        val=val,
        subtotal=subtotal,
        items_len=items_len,
        coupon=session.get('cdis', 0),
        dis=dis,
        buid=buid
    )


@app.route("/product/<pur>", methods=['POST','GET'])
@customer_required
def product(pur):
    return product_detail(pur)

@app.route("/supproduct/<pur>", methods=['POST','GET'])
@supplier_required
def supproduct(pur):
    return supproduct_detail(pur)

@app.route("/checkout", methods=['POST','GET'])
@customer_required
def checkout():
    if(request.method == 'POST'):
        return checkout_details()
    if(request.method == 'GET'):
        return normal_checkout()

@app.route("/search", methods=['POST','GET'])
@customer_required
def qsearch():
    return query_search()

@app.route("/favourites", methods=['POST','GET'])
@customer_required
def favourites():
    if (request.method == 'GET'):
        return favourite()
    if (request.method == 'POST'):
        return fav()

@app.route("/hdemo", methods=['POST', 'GET'])
def demo():
    if request.method == 'POST':
        flash("Спасибо за отзыв!!", category="success")
        return redirect(request.referrer)

@app.route("/supplier", methods=['POST','GET'])
@supplier_required
def supplier():
    if request.method == 'GET':
        return render_template("supplier.html")
    if request.method == 'POST':
        if(request.form.get('type', None) == 'add'):
            if(supadd()):
                flash("Препарат добавлен в базу!!", category="success")
            else:
                flash("Ошибка!!", category="danger")
        if(request.form.get('type', None) == 'update'):
            msg, category = supupdate()
            flash(msg, category=category)
        return redirect(request.referrer)

@app.route("/supsearch", methods=['POST','GET'])
@supplier_required
def qsearchsup():
    return ssearch()

@app.route("/ohistory/<bid>", methods=['POST','GET'])
@customer_required
def ohistory(bid):
    return orhistory(bid)

@app.route("/updatepassword", methods=['POST','GET'])
@login_required
def updatepassword():
    if request.method == 'GET':
        return render_template("password.html")
    if request.method == 'POST':
        return upass()

@app.route("/singleproduct/<pid>/<rol>", methods=['POST','GET'])
@customer_required
def singleproduct(pid, rol):
    return single_product(pid, rol)

@app.route("/cart", methods=['GET'])
@customer_required
def cart():
    items, subtotal, items_len = cart_items()
    buid = buyid()
    dis = session.get('cdis', 0)
    return render_template("cart.html", items=items, subtotal=subtotal, items_len=items_len, coupon=0, buid=buid, dis=dis)


@app.route("/cart_item", methods=['POST'])
@customer_required
def item():
    if request.method == "POST":
        if(request.form.get('type', None) == 'delete'):
            delete_item(request.form.get('item_id'))
            flash("Препарат удален!!", category="success")
        elif(request.form.get('type', None) == 'update'):
            msg, cat = update_item(request.form.get('item_id', None),
                              request.form.get('quantity', None),
                              request.form.get('med_id', None),
                              request.form.get('med_role', None))
            flash(msg, category=cat)
        else:
            add_item(request.form.get('med_id', None),
                     request.form.get('quantity', None),
                     request.form.get('med_role', None))
        return redirect(request.referrer)

@app.route("/mhome")
@customer_required
def mhome():
    categories=category_items()
    categories1=category_items()
    categories2=category_items()
    subtotal, len_items = cart_value()
    buid = buyid()
    return render_template("home.html", categories=categories,categories1=categories1, categories2=categories2, subtotal=subtotal, len_items=len_items, buid=buid)

if __name__ == "__main__":
    app.run(debug=True)