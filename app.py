from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)

app.secret_key = 'govt_scheme_secret_key'

# ---------------- MYSQL CONFIG ----------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'government_scheme_db'

mysql = MySQL(app)

# =========================================================
# LOGIN DECORATORS
# =========================================================

def login_required_member(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if 'member_id' not in session:
            return redirect(url_for('member_login'))

        return func(*args, **kwargs)

    return wrapper


def login_required_admin(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if 'admin' not in session:
            return redirect(url_for('admin_login'))

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# HOME
# =========================================================

@app.route('/')
def home():
    return render_template('home.html')


# =========================================================
# SERVICES
# =========================================================

@app.route('/services')
def services():
    return render_template('services.html')


# =========================================================
# ABOUT
# =========================================================

@app.route('/about')
def about():
    return render_template('about.html')


# =========================================================
# CONTACT
# =========================================================

@app.route('/contact')
def contact():
    return render_template('contact.html')


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        if email == 'admin@gmail.com' and password == '123':

            session['admin'] = email

            flash('Admin login successful', 'success')

            return redirect(url_for('admin_dashboard'))

        else:

            flash('Invalid admin email or password', 'danger')

    return render_template('admin_login.html')


# =========================================================
# MEMBER LOGIN
# =========================================================

@app.route('/member-login', methods=['GET', 'POST'])
def member_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM members WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            session['member_id'] = user[0]

            flash('Login successful', 'success')

            return redirect(url_for('member_dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('member_login.html')


# =========================================================
# REGISTER
# =========================================================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        caste = request.form['caste']
        userType = request.form['userType']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO members
            (name, email, password, age, gender, caste, userType)

            VALUES(%s,%s,%s,%s,%s,%s,%s)
            """,
            (name, email, password, age, gender, caste, userType)
        )

        mysql.connection.commit()

        cur.close()

        flash('Registration successful. Please login.', 'success')

        return redirect(url_for('member_login'))

    return render_template('register.html')


# =========================================================
# MEMBER DASHBOARD
# =========================================================

@app.route('/member-dashboard')
@login_required_member
def member_dashboard():
    return render_template('member_dashboard.html')


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route('/admin-dashboard')
@login_required_admin
def admin_dashboard():
    return render_template('admin_dashboard.html')


# =========================================================
# ADD SCHEME
# =========================================================

@app.route('/add-scheme', methods=['GET', 'POST'])
@login_required_admin
def add_scheme():

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        status = request.form['status']

        min_age = request.form['min_age']
        max_age = request.form['max_age']
        gender = request.form['gender']
        caste = request.form['caste']
        userType = request.form['userType']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO schemes
            (title, description, status, min_age, max_age, gender, caste, userType)

            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                title,
                description,
                status,
                min_age,
                max_age,
                gender,
                caste,
                userType
            )
        )

        mysql.connection.commit()

        cur.close()

        flash('Scheme added successfully', 'success')

        return redirect(url_for('view_schemes'))

    return render_template('add_scheme.html')


# =========================================================
# VIEW SCHEMES
# =========================================================

@app.route('/view-schemes')
def view_schemes():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM schemes")

    schemes = cur.fetchall()

    cur.close()

    return render_template('view_schemes.html', schemes=schemes)


# =========================================================
# APPLY SCHEME
# =========================================================

@app.route('/apply/<int:scheme_id>')
@login_required_member
def apply_scheme(scheme_id):

    member_id = session.get('member_id')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT * FROM applications
        WHERE member_id=%s AND scheme_id=%s
        """,
        (member_id, scheme_id)
    )

    existing_application = cur.fetchone()

    if existing_application:

        cur.close()

        flash('You already applied for this scheme', 'warning')

        return redirect(url_for('view_schemes'))

    cur.execute(
        """
        INSERT INTO applications
        (member_id, scheme_id, status)

        VALUES(%s,%s,%s)
        """,
        (member_id, scheme_id, 'pending')
    )

    mysql.connection.commit()

    cur.close()

    flash('Application submitted successfully', 'success')

    return redirect(url_for('view_schemes'))


# =========================================================
# VIEW APPLICATIONS
# =========================================================

@app.route('/view-applications')
@login_required_admin
def view_applications():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM applications")

    applications = cur.fetchall()

    cur.close()

    return render_template(
        'view_applications.html',
        applications=applications
    )


# =========================================================
# APPROVE APPLICATION
# =========================================================

@app.route('/approve/<int:application_id>')
@login_required_admin
def approve_application(application_id):

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE applications SET status=%s WHERE id=%s",
        ('approved', application_id)
    )

    mysql.connection.commit()

    cur.close()

    flash('Application approved successfully', 'success')

    return redirect(url_for('view_applications'))


# =========================================================
# REJECT APPLICATION
# =========================================================

@app.route('/reject/<int:application_id>')
@login_required_admin
def reject_application(application_id):

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE applications SET status=%s WHERE id=%s",
        ('rejected', application_id)
    )

    mysql.connection.commit()

    cur.close()

    flash('Application rejected', 'danger')

    return redirect(url_for('view_applications'))


# =========================================================
# ADD QUERY
# =========================================================

@app.route('/add-query', methods=['GET', 'POST'])
@login_required_member
def add_query():

    if request.method == 'POST':

        member_id = session.get('member_id')

        scheme_id = request.form['scheme_id']

        message = request.form['message']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO queries
            (member_id, scheme_id, message, reply)

            VALUES(%s,%s,%s,%s)
            """,
            (member_id, scheme_id, message, '')
        )

        mysql.connection.commit()

        cur.close()

        flash('Query submitted successfully', 'success')

        return redirect(url_for('my_queries'))

    return render_template('add_query.html')


# =========================================================
# MY QUERIES
# =========================================================

@app.route('/my-queries')
@login_required_member
def my_queries():

    member_id = session.get('member_id')

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM queries WHERE member_id=%s",
        (member_id,)
    )

    queries = cur.fetchall()

    cur.close()

    return render_template(
        'my_queries.html',
        queries=queries
    )


# =========================================================
# VIEW QUERIES
# =========================================================

@app.route('/view-queries')
@login_required_admin
def view_queries():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM queries")

    queries = cur.fetchall()

    cur.close()

    return render_template(
        'view_queries.html',
        queries=queries
    )


# =========================================================
# REPLY QUERY
# =========================================================

@app.route('/reply/<int:query_id>', methods=['GET', 'POST'])
@login_required_admin
def reply_query(query_id):

    if request.method == 'POST':

        reply = request.form['reply']

        cur = mysql.connection.cursor()

        cur.execute(
            "UPDATE queries SET reply=%s WHERE id=%s",
            (reply, query_id)
        )

        mysql.connection.commit()

        cur.close()

        flash('Reply submitted successfully', 'success')

        return redirect(url_for('view_queries'))

    return render_template(
        'reply_query.html',
        query_id=query_id
    )


# =========================================================
# MATCH SCHEMES
# =========================================================

@app.route('/match-schemes')
@login_required_member
def match_schemes():

    member_id = session.get('member_id')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT age, gender, caste, userType
        FROM members
        WHERE id=%s
        """,
        (member_id,)
    )

    member = cur.fetchone()

    if not member:

        cur.close()

        return "Member not found"

    age = member[0] if member[0] is not None else 0

    gender = (member[1] or "any").lower()

    caste = (member[2] or "any").lower()

    userType = (member[3] or "any").lower()

    cur.execute(
        "SELECT * FROM schemes WHERE status='running'"
    )

    schemes = cur.fetchall()

    matched = []

    for s in schemes:

        if not s or len(s) < 9:
            continue

        min_age = int(s[4]) if s[4] not in [None, ''] else 0

        max_age = int(s[5]) if s[5] not in [None, ''] else 100

        s_gender = (s[6] or "any").lower()

        s_caste = (s[7] or "any").lower()

        s_type = (s[8] or "any").lower()

        if (

            age >= min_age and
            age <= max_age and

            (s_gender == gender or s_gender == "any") and

            (s_caste == caste or s_caste == "any") and

            (s_type == userType or s_type == "any")

        ):

            matched.append(s)

    cur.close()

    return render_template(
        'view_schemes.html',
        schemes=matched
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route('/logout')
def logout():

    session.clear()

    flash('Logged out successfully', 'info')

    return redirect(url_for('home'))


# =========================================================
# RUN APP
# =========================================================

if __name__ == '__main__':
    app.run(debug=True)
