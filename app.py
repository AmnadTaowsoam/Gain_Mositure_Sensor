from flask import Flask, render_template, request, redirect, url_for,session,g,Response
from my_function.MoistureSensor import MoistureSensor
import plotly.io as pio
import time
from my_db.CornMoistDB import CornMoistDB

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Replace with your own secret key
db = CornMoistDB()


@app.before_request
def before_request():
    try:
        user = session['username']
        g.user = user
    except:
        print("session error")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['user_email']
        password = request.form['user_password']
        plant = request.form['plant']
        # Perform login logic here (e.g., check credentials against a database)
        condition = f"email='{email}' AND password='{password}'"
        user = db.select_data('users', condition=condition)
        if user:
            session['user_id'] = user[0][0]  # Store the user ID in the session
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['user_email']
        password = request.form['user_password']
        plant = request.form['plant']
        # Perform registration logic here (e.g., save user information in a database)
        columns = ['user_name', 'email', 'password','plant']
        values = [user_name, email, password, plant]
        db.insert_into_table('users', columns, values)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Get the user's information from the database
    condition = f"id={user_id}"
    user = db.select_data('users', condition=condition)[0]
    return render_template('home.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inspection_lot = request.form['inspection_lot']
        material = request.form['material']
        batch = request.form['batch']
        plant = request.form['plant']

        sensor = MoistureSensor()
        moisture_percentages = []
        
        for i in range(10):
            data = sensor.read_data()
            if data:
                filtered_data = [value for value in data if value > 800]
                moisture_percentage = sensor.calculate_moisture_percentage(filtered_data)
                moisture_percentages.extend(moisture_percentage)
            time.sleep(1)

        fig = sensor.plot_moisture_percentage(moisture_percentages)
        plot_html = pio.to_html(fig, full_html=False)
        stats = sensor.calculate_stats()
        
        # Insert MoistureRecord into database
        values = [
            inspection_lot,
            material,
            batch,
            plant,
            stats[0],
            stats[1],
            stats[2],
            stats[3],
            stats[4]
        ]
        db.insert_into_table('MoistureRecord', values=values)

        return render_template('index.html', plot_html=plot_html, stats=stats)

    return render_template('index.html')

if __name__ == '__main__':
    # Create the users table if it doesn't exist
    if not db.select_data('INFORMATION_SCHEMA.TABLES', "TABLE_NAME='users'"):
        db.create_table('users', ['id INT IDENTITY(1,1) PRIMARY KEY', 'user_name NVARCHAR(50)', 'email NVARCHAR(50)', 'password NVARCHAR(50)','plant NVARCHAR(50)'])
        
    app.run(host='0.0.0.0', port=8000, debug=True)