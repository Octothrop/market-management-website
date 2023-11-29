from flask import Flask, render_template, request, session, jsonify
from database import insert_db
from database import get_db, get_user_id
from sqlalchemy import create_engine, text

app = Flask(__name__)
db_string = "mysql+pymysql://6dodeptmo0rbxmzr2qms:pscale_pw_6UHZHXqyci9GtuVL38R7l7tJxmIcOihvuxtv9heGRVB@aws.connect.psdb.cloud/test_flask?charset=utf8mb4"

engine = create_engine(
    db_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
)

app.secret_key = 'your_secret_key'

@app.route("/")
def home_test():
  return render_template("home.html")

@app.route("/redirect")
def redirect_test():
  return render_template("login.html")

@app.route("/register")
def register():
    return render_template('register.html')

  
@app.route("/login")
def login():
  return render_template('login.html')

@app.route("/register_form", methods=['POST'])
def register_form():
  data = request.form
  username = data.get('ru')
  password = data.get('rp')
  confirm_password = data.get('crp')
  phone_number = data.get('ph')
    

  with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM USER WHERE username = :user"),
                                user=username)
            existing_user = result.fetchone()

            if existing_user:
               return render_template('register.html', message="Username already exists", s=True)

            if password != confirm_password:
                return render_template('register.html', message="Passwords do not match", s=True)

            result1 = conn.execute(text("SELECT * FROM USER WHERE uphone = :ph"),
                                ph=phone_number)
            existing_phone_number = result1.fetchone()

            if existing_phone_number:
                 return render_template('register.html', message="Phone number already exists", s=True)

  
  insert_db()
  return render_template('login.html')

@app.route("/login_form", methods=['POST'])
def loform():
  role = request.form.get('ur')
  uname = request.form.get('ru')
  
  if get_db() == True:
    return render_template(f'{role}.html',success=True, username = uname)
  else :
    return render_template('login.html', success=False)

@app.route('/profile/<string:username>')
def profile(username):
    uname1 = username
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM USER WHERE username = :user"), user=uname1)
        print(result)
        user_profile = result.fetchone()
        print(user_profile)
    return render_template('profile.html', user_profile = user_profile, username = username)

@app.route('/connection/<string:username>')
def connection(username):
    uname2 = username
    with engine.connect() as conn:
        result = conn.execute(text("SELECT U.username, U.urole FROM USER U WHERE U.userid IN (SELECT C.Suid FROM CONNECTION C WHERE C.Muid IN (SELECT X.userid FROM USER X WHERE X.username = :user)) "), user=uname2)
        print(result)
        user_connection = result.fetchall()
    print(user_connection)
    return render_template('connection.html', connection = user_connection, username = uname2)

@app.route('/returner/<string:username>')
def returner(username):
  unamer = username
  with engine.connect() as conn:
      result = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=unamer)
      ugetrole = result.fetchone()

  roler = ugetrole.urole
  print(roler)
  return render_template(f'{roler}.html', username=unamer)

@app.route('/sales/<string:username>')
def sales(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM CROP"))
        crops = result.fetchall()
        result1 = conn.execute(text("SELECT S.cropid, C.cname, S.sqty, S.sprice FROM SALES S JOIN CROP C ON S.cropid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username)"), username=username)
        sales_data = result1.fetchall()

    return render_template('sales.html', crops=crops, username = username, sales_data=sales_data)

@app.route('/submit_sales/<string:username>', methods=['POST'])
def submit_sales(username):
    crop_id = request.form.get('crop')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    seller_uid = get_user_id(username)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM SALES"))
        count_result = result.fetchone()[0]
        sid = f"s{count_result + 1}"
       
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO SALES (sid, cropid, sqty, sprice, suid) "
                          "VALUES (:sid, :cropid, :sqty, :sprice, :suid)"),
                     sid=sid, cropid=crop_id, sqty=quantity, sprice=price, suid=seller_uid)
        result = conn.execute(text("SELECT * FROM CROP"))
        crops = result.fetchall()
        result1 = conn.execute(text("SELECT S.cropid, C.cname, S.sqty, S.sprice FROM SALES S JOIN CROP C ON S.cropid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username)"), username=username)
        sales_data = result1.fetchall()

        return render_template('sales.html', crops=crops, username = username, sales_data=sales_data)

@app.route('/get_farmer_count')
def get_farmer_count():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM USER WHERE urole ='farmer'"))
        count = result.scalar()
        print(count)

    return jsonify({'count': count})


"""
@app.route('/history/<string:username>')
def profile(username): 
    uname3 = username
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM USER WHERE username = :user"), user=uname3)
        print(result)
        user_profile = result.fetchone()
        print(user_profile)
    return render_template('profile.html', user_profile = user_profile)

@app.route('/inventory/<string:username>')
def profile(username):
    uname4 = username
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM USER WHERE username = :user"), user=uname4)
        print(result)
        user_profile = result.fetchone()
        print(user_profile)
    return render_template('profile.html', user_profile = user_profile)"""

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)