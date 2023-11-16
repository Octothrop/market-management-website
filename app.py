from flask import Flask, render_template, request
from database import insert_db
from database import get_db
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

@app.route("/")
def home_test():
  return render_template("home.html")

@app.route("/redirect")
def redirect_test():
  return render_template("login.html")

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/reg_email", methods=['GET'])
def reg_email():
  d = request.form
  em = d.get('txtb')
  print(em)
  if em !=  None:
    with engine.connect() as conn:
       result = conn.execute(text("INSERT INTO EBOX (email)"
                                 "(VALUES (:em)"),
           em=em)
  return render_template("home.html")
  
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
            result = conn.execute(text("SELECT * FROM User WHERE username = :user"),
                                user=username)
            existing_user = result.fetchone()

            if existing_user:
               return render_template('register.html', message="Username already exists", s=True)

            if password != confirm_password:
                return render_template('register.html', message="Passwords do not match", s=True)

            result1 = conn.execute(text("SELECT * FROM User WHERE phone_number = :ph"),
                                ph=phone_number)
            existing_phone_number = result1.fetchone()

            if existing_phone_number:
                 return render_template('register.html', message="Phone number already exists", s=True)

  
  insert_db()
  return render_template('login.html')

@app.route("/login_form", methods=['POST'])
def loform():
  if get_db() == True:
    return render_template('home.html', success=True)
  else :
    return render_template('login.html', success=False)

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)