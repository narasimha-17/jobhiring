from flask import Flask, request, render_template , jsonify , redirect, url_for, session, flash
from database import engine  , load_jobs_from_db, load_job_from_db , add_application_to_db , get_application_by_id,get_applications , insert_job_to_db, get_user_from_db , add_user_to_db, get_user_applications,  has_user_applied ,get_recruiter_by_email, get_jobs_by_recruiter
from werkzeug.security import check_password_hash, generate_password_hash  
from sqlalchemy import text 
import database



app=Flask(__name__)
app.secret_key = 'your_secret_key'




def load_jobs_from_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM jobs"))
        jobs=[]
        for row in result.all():
            jobs.append(dict(row._mapping))
        return jobs




@app.route('/')
def home():
    jobs=load_jobs_from_db()
    return render_template('home.html'
                           ,jobs=jobs)


@app.route("/job/<int:id>")
def get_job(id):
    job = load_job_from_db(id)
    return render_template('jobpage.html', job=job)

@app.route("/job/<id>/apply", methods=["post"])
def apply_to_job(id):
    data=request.form
    job=load_job_from_db(id)
    add_application_to_db(id,data)
    # Add application to database
    return render_template('applicationsubmitted.html',application=data, job=job)   





@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_db(username)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))  # Redirect to a protected page
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)




@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        existing_user = get_user_from_db(username)
        if existing_user:
            error = "Username already taken. Please choose a different one."
        else:
            if add_user_to_db(username, hashed_password):
                return redirect(url_for('login'))
            else:
                error = "Registration failed."
    return render_template('register.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        applications = get_user_applications(user_id)
        # saved_jobs = get_user_saved_jobs(user_id) # Uncomment if you implement saved jobs
        return render_template('dashboard.html', applications=applications, saved_jobs=None) # Pass the applications data
    return redirect(url_for('login'))



@app.route('/postjob', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        salary = request.form.get('salary')
        currency = request.form.get('currency')
        responsibilities = request.form['responsibilities']
        requirements = request.form['requirements']

        if insert_job_to_db(title, location, salary, currency, responsibilities, requirements):
            return redirect(url_for('home'))
        else:
            error_message = "Failed to post the job. Please try again."
            return render_template('postjob.html', error_message=error_message)

    return render_template('postjob.html')


@app.route('/recruiter/login', methods=['GET', 'POST'])
def recruiter_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        recruiter = database.get_recruiter_by_email(email)

        if recruiter is None or not check_password_hash(recruiter['password'], password):
            error = 'Invalid email or password.'

        if error is None:
            session['recruiter_id'] = recruiter['id']
            flash('Logged in as recruiter!')
            return redirect(url_for('recruiter_selection'))
        else:
            flash(error)
    return render_template('recruiter_selection.html')


@app.route('/recruiter/selection')
def recruiter_selection():
    if 'recruiter_id' in session:
        applications = database.get_applications() # Example: Fetch all applications
        jobs = database.get_jobs_by_recruiter(session['recruiter_id']) # Example: Fetch recruiter's jobs
        return render_template('recruiter_selection.html', applications=applications, jobs=jobs)
    else:
        flash('You must be logged in as a recruiter to access this page.')
        return redirect(url_for('recruiter_login.html'))


@app.route('/recruiter/logout')
def recruiter_logout():
    session.pop('recruiter_id', None)
    flash('Logged out as recruiter.')
    return redirect(url_for('home'))


@app.route('/recruiter/jobs')
def view_posted_jobs():
    if 'recruiter_id' in session:
        recruiter_id = session['recruiter_id']
        jobs = database.get_jobs_by_recruiter(recruiter_id)
        return render_template('view_posted_jobs.html', jobs=jobs)
    else:
        flash('You must be logged in as a recruiter to access this page.')
        return redirect(url_for('recruiter_login'))



@app.route("/api/jobs")
def list_jobs():
    return jsonify(load_jobs_from_db())


                        

if __name__ == '__main__':
    app.run(debug=True)