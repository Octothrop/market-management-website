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
  print(role)
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

@app.route('/returner/<string:username>')
def returner(username):
  unamer = username
  with engine.connect() as conn:
      result = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=unamer)
      ugetrole = result.fetchone()

  roler = ugetrole.urole
  print(roler)
  return render_template(f'{roler}.html', username=unamer)

@app.route('/sell/<string:username>')
def sell(username):
  with engine.connect() as conn:
      result1 = conn.execute(text("SELECT S.iid, C.cname, S.iqty, S.exp FROM INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) AND S.strack IS FALSE AND S.exp >= CURDATE() AND S.iid NOT IN (SELECT I.iid FROM SALES I)"), username=username)
      sales = result1.fetchall()
      result2 = conn.execute(text("SELECT C.cname, S.iqty, S.exp, I.sprice FROM SALES I, INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) AND S.strack IS FALSE AND S.exp >= CURDATE() AND I.iid = S.iid"), username=username)
      salesx = result2.fetchall()

      print(salesx)
  return render_template('sell.html', username=username, sales_data = sales, sales_datax = salesx)

@app.route('/sales/<string:username>')
def sales(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM CROP"))
        crops = result.fetchall()
        result1 = conn.execute(text("SELECT S.icid, C.cname, S.iqty, S.exp, S.iid NOT IN (SELECT I.iid FROM SALES I) AS not_in_sales, S.exp >= CURDATE() AS timed_data, S.strack FROM INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) "), username=username)
        sales_data = result1.fetchall()
        result3 = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
        ugetrole = result3.fetchone()
        print(sales_data)
        print(ugetrole[0])

    return render_template('sales.html', crops=crops, username = username, sales_data=sales_data, role=ugetrole[0])

@app.route('/submit_sales/<string:username>', methods=['POST'])
def submit_sales(username):
    crop_id = request.form.get('crop')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    seller_uid = get_user_id(username)
    date_exp = request.form.get('expiry')
       
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO INVENTORY (icid, iqty, exp, suid) "
                 "VALUES (:icid, :iqty, :exp, :suid)"),
            icid=crop_id, iqty=quantity, exp=date_exp, suid=seller_uid
        )
        result3 = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
        ugetrole = result3.fetchone()
        result = conn.execute(text("SELECT * FROM CROP"))
        crops = result.fetchall()
        result1 = conn.execute(text("SELECT S.icid, C.cname, S.iqty, S.exp , S.iid NOT IN (SELECT I.iid FROM SALES I) AS not_in_sales, S.exp >= CURDATE() AS timed_data, S.strack FROM INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) "), username=username)
        sales_data = result1.fetchall()
        print(sales_data)

        return render_template('sales.html', crops=crops, username = username, sales_data=sales_data, role=ugetrole[0])

@app.route('/get_farmer_count')
def get_farmer_count():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM USER WHERE urole ='farmer'"))
        count = result.scalar()
        print(count)

    return jsonify({'count': count})

@app.route('/get_agent_count')
def get_agent_count():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM USER WHERE urole ='agent'"))
        count = result.scalar()
        print(count)

    return jsonify({'count': count})

@app.route('/get_buyer_count')
def get_buyer_count():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM USER WHERE urole ='buyer'"))
        count = result.scalar()
        print(count)

    return jsonify({'count': count})

@app.route('/submit_sell/<string:username>', methods=['POST'])
def submit_sell(username):

      iids = request.form.get('sale')
      sprices = request.form.get('price')
      print(iids)
      with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO SALES (iid, sprice) "
                     "VALUES (:iid, :sprice)"),
                iid = iids, sprice = sprices
            )
            result1 = conn.execute(text("SELECT S.iid, C.cname, S.iqty, S.exp FROM INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) AND S.strack IS FALSE AND S.exp >= CURDATE() AND S.iid NOT IN (SELECT I.iid FROM SALES I)"), username=username)
            result2 = conn.execute(text("SELECT C.cname, S.iqty, S.exp, I.sprice FROM SALES I, INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) AND S.strack IS FALSE AND S.exp >= CURDATE() AND S.iid = I.iid"), username=username)
            sales = result1.fetchall()
            salesx = result2.fetchall()
            print(salesx)
      return render_template('sell.html', username=username, sales_data = sales, sales_datax = salesx)

@app.route('/connection/<string:username>')
def connection(username):
    uname2 = username

    with engine.connect() as conn:
        result1 = conn.execute(text("SELECT U.userid FROM USER U WHERE U.username = :user"), user=uname2)
        uid = result1.fetchone()
        resultx = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=uname2)
        ugetrole = resultx.fetchone()
        print("uid :==> ",uid)
        result = conn.execute(text("""
            SELECT U.username, U.urole,
                   CASE
                       WHEN C.Muid IS NOT NULL OR C.Suid IS NOT NULL THEN 'Connected'
                       ELSE 'Not Connected'
                   END AS connected_status
            FROM USER U
            LEFT JOIN CONNECTION C ON (C.Muid = U.userid AND C.Suid = :user) 
            WHERE U.userid NOT IN (SELECT userid FROM USER WHERE username = :user)
        """), user=uid[0])

        user_connection = result.fetchall()
    print(user_connection)
    return render_template(f'connection_{ugetrole[0].lower()}.html', users=user_connection, username=uname2, role=ugetrole[0])

@app.route('/connect_me/<string:username>', methods=['POST'])
def connect_me(username):

      muid = username
      suid = request.form.get('userx')
      with engine.connect() as conn:
            resultx = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
            ugetrole = resultx.fetchone()
            result1 = conn.execute(text("SELECT U.userid FROM USER U WHERE U.username = :user"), user=muid)
            result2 = conn.execute(text("SELECT U.userid FROM USER U WHERE U.username = :user"), user=suid)
            Muid = result1.fetchone()
            Suid = result2.fetchone()
            conn.execute(text("INSERT INTO CONNECTION (Muid, Suid) "
                 "VALUES (:Muid, :Suid)"),
            Muid = Muid[0], Suid = Suid[0] );
            conn.execute(text("INSERT INTO CONNECTION (Muid, Suid) "
                 "VALUES (:Muid, :Suid)"),
            Muid = Suid[0], Suid = Muid[0] );
            result3 = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
            ugetrole = result3.fetchone()
            print("uid :==> ",Muid[0])
            result = conn.execute(text("""
                SELECT U.username, U.urole,
                       CASE
                           WHEN C.Muid IS NOT NULL OR C.Suid IS NOT NULL THEN 'Connected'
                           ELSE 'Not Connected'
                       END AS connected_status
                FROM USER U
                LEFT JOIN CONNECTION C ON (C.Muid = U.userid AND C.Suid = :user)
                WHERE U.userid NOT IN (SELECT userid FROM USER WHERE username = :user)
            """), user=Muid[0])
            user_connection = result.fetchall()
            print(user_connection)
            print(ugetrole)
      return render_template(f'connection_{ugetrole[0].lower()}.html', users=user_connection, username=username, role=ugetrole[0])



@app.route('/buy/<string:username>')
def buy(username):

        current_user = username
        with engine.connect() as conn:
            resultx = conn.execute(text("SELECT U.userid FROM USER U WHERE U.username = :user"), user=current_user)
            id = resultx.fetchone()

            result = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
            ugetrole = result.fetchone()
            # Get the list of connected agents
            result_agents = conn.execute(
                text("SELECT Suid FROM CONNECTION WHERE Muid = (SELECT userid FROM USER WHERE username = :user)"),
                user=current_user
            )
            connected_agents = [row['Suid'] for row in result_agents.fetchall()]
        
            if not connected_agents:
                # No connected agents, you can choose to render a different template or display a message
                return render_template('na.html', username=current_user, role=ugetrole)
        
            # Fetch sales data for connected agents' inventory
            result = conn.execute(text("""
                SELECT S.sid, C.cname AS crop_name, U.username AS farmer_name, U.userid, S.sprice, I.iqty
                FROM SALES S
                JOIN INVENTORY I ON S.iid = I.iid
                JOIN CROP C ON I.icid = C.cropID
                JOIN USER U ON I.suid = U.userid
                WHERE I.strack IS FALSE AND I.exp >= CURDATE()
                AND I.suid IN :connected_agents
            """), connected_agents=tuple(connected_agents))

            print(ugetrole)
            sales_data = result.fetchall()
            if sales_data == []:
              return render_template('na.html', username=current_user, role=ugetrole)
        
        return render_template('buy.html', username=current_user, sales_data=sales_data, userid = id[0])


@app.route('/request_sale/<string:username>', methods=['POST'])
def request_sale(username):
    current_user = username
    sale_id = request.form.get('sale_id')
    user_id = request.form.get('user_id')
    

    with engine.connect() as conn:

          result = conn.execute(text("SELECT U.urole FROM USER U WHERE U.username = :user"), user=username)
          ugetrole = result.fetchone()
          resultx = conn.execute(text("SELECT U.userid FROM USER U WHERE U.username = :user"), user=current_user)
          id = resultx.fetchone()
          # Step 1: Update the strack for the buyer
          conn.execute(text("UPDATE INVENTORY SET strack = TRUE WHERE iid IN (SELECT iid FROM SALES WHERE sid = :sid)"), sid = sale_id)
  
          # Step 2: Insert a new record for the requested user
          conn.execute(text("INSERT INTO INVENTORY (icid, iqty, exp, suid) "
                            "SELECT icid, iqty, exp, :requser_id "
                            "FROM INVENTORY WHERE suid = :user_id"), requser_id=id[0], user_id=user_id)
      # Get the list of connected agents
          result_agents = conn.execute(
              text("SELECT Suid FROM CONNECTION WHERE Muid = (SELECT userid FROM USER WHERE username = :user)"),
              user=current_user
          )
          connected_agents = [row['Suid'] for row in result_agents.fetchall()]
          print(ugetrole)
          if not connected_agents:
              # No connected agents, you can choose to render a different template or display a message
              return render_template('na.html', username=current_user, role=ugetrole)

          # Fetch sales data for connected agents' inventory
          result = conn.execute(text("""
              SELECT S.sid, C.cname AS crop_name, U.username AS farmer_name, U.userid, S.sprice, I.iqty
              FROM SALES S
              JOIN INVENTORY I ON S.iid = I.iid
              JOIN CROP C ON I.icid = C.cropID
              JOIN USER U ON I.suid = U.userid
              WHERE I.strack IS FALSE AND I.exp >= CURDATE()
              AND I.suid IN :connected_agents
          """), connected_agents=tuple(connected_agents))

          sales_data = result.fetchall()
          if sales_data == []:
            return render_template('na.html', username=current_user, role=ugetrole)

    return render_template('buy.html', username=current_user, sales_data=sales_data, userid = id[0])

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

@app.route('/invent/<string:username>')
def invent(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM CROP"))
        crops = result.fetchall()
        result1 = conn.execute(text("SELECT S.icid, C.cname, S.iqty, S.exp, S.iid NOT IN (SELECT I.iid FROM SALES I) AS not_in_sales, S.exp >= CURDATE() AS timed_data, S.strack FROM INVENTORY S JOIN CROP C ON S.icid = C.cropID WHERE S.suid = (SELECT U.userid FROM USER U WHERE U.username = :username) "), username=username)
        sales_data = result1.fetchall()

        print(sales_data)

    return render_template('buyer_invent.html', username=username, sales_data=sales_data)

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)