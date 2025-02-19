from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb,random,datetime
from flask_bcrypt import Bcrypt
from flask import Flask

from random import randint

connection = mysql.connector.connect(host="localhost",database='ph', user="root", passwd="parol")

app = Flask(__name__)
app.secret_key = "super secret key"
purpose = ["Витамины", "Аминокислоты", "Селен", "Обезболивающие", "Слабительное", "Противоаллергенные", "Кат7", "Кат8"]
supplier = ["Поставщик1", "Поставщик2", "Поставщик3", "Поставщик4", "Поставщик5", "Поставщик6", "Поставщик7"]
mtype = ["Отечественный", "Зарубежный"]
df = ["3 раза в день", "2 раза в день", "1 один раз в день перед сном", "Раз в неделю", "При сильной боли ", "При боли "]
cur = connection.cursor()
start_date = datetime.date(2021, 1, 1)
end_date = datetime.date(2027, 5, 1)
time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days
random_number_of_days = random.randrange(days_between_dates)
for i in range(1,301):
    date=datetime.date(randint(2020,2030), randint(1,12), randint(1,28))
    date1=datetime.date(randint(2020,2030), randint(1,12), randint(1,28))
    p=random.choice(purpose)
    x=random.randint(50,600)
    d=random.choice(df)
    s=random.choice(supplier)
    cur.execute("INSERT INTO medicine(med_id,med_name,med_brandname,med_purpose,med_expiry,dosage_form,med_price,med_role,med_quantity,med_supplier) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",( i, "med"+str(i), "brand"+str(i), str(p), str(date), str(d), str(x), "local", str(randint(10,300)), str(s)))
    cur.execute("INSERT INTO medicine(med_id,med_name,med_brandname,med_purpose,med_expiry,dosage_form,med_price,med_role,med_quantity,med_supplier) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",( i, "med"+str(i), "brand"+str(i+1), str(p), str(date1), str(d), str(x/3), "generic", str(randint(10,300)), str(s)))
bcrypt = Bcrypt(app)



# for i in range(7,13):
#     hashed_pass = bcrypt.generate_password_hash("user"+str(i)).decode('utf-8')
#     cur.execute("INSERT INTO login(user_email, user_pass, user_first_name, user_last_name, user_address, user_category) VALUES(%s, %s, %s, %s, %s, %s)",("user"+str(i)+"@gmail.com", hashed_pass, "User", str(i), "address"+str(i), "customer"))
#
#
# for i in range(1,7):
#     hashed_pass = bcrypt.generate_password_hash("supplier"+str(i)).decode('utf-8')
#     cur.execute("INSERT INTO login(user_email, user_pass, user_first_name, user_last_name, user_address, user_category) VALUES(%s, %s, %s, %s, %s, %s)",("supplier"+str(i)+"@gmail.com", hashed_pass, "Supplier"+str(i), str(i), "address"+str(i), "supplier"))


connection.commit()
cur.close()

