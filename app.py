from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'carbontracker2026'

# Database path
DB_PATH = 'carbon.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS User (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Household (
            HProfileID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Size INTEGER NOT NULL,
            Location TEXT NOT NULL,
            FOREIGN KEY (UserID) REFERENCES User(UserID)
        );
        CREATE TABLE IF NOT EXISTS Category (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT NOT NULL,
            EmissionFactor REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Activity (
            ActivityID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            CategoryID INTEGER NOT NULL,
            Amount REAL NOT NULL,
            Date TEXT NOT NULL,
            FOREIGN KEY (UserID) REFERENCES User(UserID),
            FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
        );
        CREATE TABLE IF NOT EXISTS Recommendation (
            RecommendationID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryID INTEGER NOT NULL,
            Message TEXT NOT NULL,
            Threshold REAL NOT NULL,
            FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
        );
        INSERT OR IGNORE INTO Category (CategoryID, CategoryName, EmissionFactor) VALUES
            (1, 'Electricity', 0.2307),
            (2, 'Natural Gas', 0.1882),
            (3, 'Transport', 0.1704),
            (4, 'Water', 0.149);
        INSERT OR IGNORE INTO Recommendation (CategoryID, Message, Threshold) VALUES
            (1, 'Your electricity usage is high. Consider switching to LED lighting and using appliances during off-peak hours.', 50),
            (2, 'Your gas usage is high. Try reducing your thermostat by 1 degree to save up to 10% on emissions.', 40),
            (3, 'Your transport emissions are high. Consider using public transport or carpooling.', 30),
            (4, 'Your water usage is high. Try taking shorter showers and fixing any leaks.', 10);
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template('login.html', error='Please fill in all fields.')
        conn = get_db()
        user = conn.execute('SELECT * FROM User WHERE Username=? AND Password=?',
                          (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['UserID']
            session['username'] = user['Username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Incorrect username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        size = request.form['size']
        location = request.form['location']
        if not username or not password or not confirm or not size or not location:
            return render_template('register.html', error='Please fill in all fields.')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match.')
        try:
            conn = get_db()
            conn.execute('INSERT INTO User (Username, Password) VALUES (?, ?)',
                        (username, password))
            conn.commit()
            user = conn.execute('SELECT * FROM User WHERE Username=?',
                              (username,)).fetchone()
            conn.execute('INSERT INTO Household (UserID, Size, Location) VALUES (?, ?, ?)',
                        (user['UserID'], size, location))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='Username already exists.')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
 # Calculation of total emissions per category
 # Warning shown if total exceeds UK average of 200kg CO2e
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    activities = conn.execute('''
        SELECT a.*, c.CategoryName, c.EmissionFactor,
               (a.Amount * c.EmissionFactor) as Emissions
        FROM Activity a
        JOIN Category c ON a.CategoryID = c.CategoryID
        WHERE a.UserID = ?
    ''', (session['user_id'],)).fetchall()

    totals = {'Electricity': 0, 'Natural Gas': 0, 'Transport': 0, 'Water': 0}
    total_emissions = 0
    for a in activities:
        totals[a['CategoryName']] += a['Emissions']
        total_emissions += a['Emissions']
    conn.close()
    return render_template('dashboard.html', totals=totals,
                         total_emissions=round(total_emissions, 2),
                         username=session['username'])

@app.route('/add_activity', methods=['GET', 'POST'])
def add_activity():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        category_id = request.form['category_id']
        amount = request.form['amount']
        date = request.form['date']
        if not category_id or not amount or not date:
            conn = get_db()
            categories = conn.execute('SELECT * FROM Category').fetchall()
            conn.close()
            return render_template('addactivity.html', error='Please fill in all fields.', categories=categories)
        try:
            amount = float(amount)
            if amount <= 0:
                conn = get_db()
                categories = conn.execute('SELECT * FROM Category').fetchall()
                conn.close()
                return render_template('addactivity.html', error='Amount must be positive.', categories=categories)
        except:
            conn = get_db()
            categories = conn.execute('SELECT * FROM Category').fetchall()
            conn.close()
            return render_template('addactivity.html', error='Please enter a valid amount.', categories=categories)
        conn = get_db()
        conn.execute('INSERT INTO Activity (UserID, CategoryID, Amount, Date) VALUES (?, ?, ?, ?)',
                    (session['user_id'], category_id, amount, date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    conn = get_db()
    categories = conn.execute('SELECT * FROM Category').fetchall()
    conn.close()
    return render_template('addactivity.html', categories=categories)

@app.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    activities = conn.execute('''
        SELECT a.*, c.CategoryName, c.EmissionFactor,
               (a.Amount * c.EmissionFactor) as Emissions
        FROM Activity a
        JOIN Category c ON a.CategoryID = c.CategoryID
        WHERE a.UserID = ?
        ORDER BY a.Date DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('summary.html', activities=activities)

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    activities = conn.execute('''
        SELECT c.CategoryName, SUM(a.Amount * c.EmissionFactor) as TotalEmissions
        FROM Activity a
        JOIN Category c ON a.CategoryID = c.CategoryID
        WHERE a.UserID = ?
        GROUP BY c.CategoryName
    ''', (session['user_id'],)).fetchall()

    recos = []
    for a in activities:
        reco = conn.execute('''
            SELECT r.Message, c.CategoryName
            FROM Recommendation r
            JOIN Category c ON r.CategoryID = c.CategoryID
            WHERE c.CategoryName = ? AND ? > r.Threshold
        ''', (a['CategoryName'], a['TotalEmissions'])).fetchone()
        if reco:
            recos.append(reco)
    conn.close()
    return render_template('recommendations.html', recommendations=recos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
