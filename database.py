import sqlalchemy
from sqlalchemy import create_engine , text
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine = create_engine("mysql+mysqlconnector://root:Surya7075@localhost:3306/SRMCarrers", echo=True)

def load_jobs_from_db():
   
    # con
 with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM jobs"))
    jobs=[]
    for row in result.all():
        jobs.append(dict(row))
    return jobs
   
def load_job_from_db(id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM jobs WHERE id = :val"),
            {"val": id}
        )
        rows = result.all()
        if len(rows) == 0:
            return None
        else:
            return dict(rows[0]._mapping)  # ✅ convert to dictionary
                   
def add_application_to_db(job_id,data):
    with engine.connect() as connection:
      user_id = session.get('user_id')  # Get user_id from the session

      if user_id is None:
            # Handle the case where the user is not logged in
            print("Error: User not logged in while trying to apply.")
            return False
      query= text("INSERT INTO applications (job_id,full_name,email, resumeurl,user_id) VALUES (:job_id,:full_name,:email,:resumeurl,:user_id)")
      
      connection.execute(query, {
        "job_id": job_id,
        "full_name": data["fullname"],
        "email": data["email"],
        "resumeurl": data["resume"],
         "user_id": data["user_id"] 
      })
      connection.commit()  
      return True  # Indicate success                       
        
        
def get_user_from_db(username):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, username, password FROM users WHERE username = :username"),
            {"username": username},
        )
        user = result.fetchone()
        if user:
            return {"id": user[0], "username": user[1], "password": user[2]}
        return None
    


def add_user_to_db(username, password):
    with engine.connect() as connection:
        try:
            query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
            connection.execute(query, {"username": username, "password": password})
            connection.commit()
            return True
        except Exception as e:
            print(f"Error adding user to database: {e}")
            return False


def get_user_applications(user_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                 
                  a.user_id , a.id,
                    a.job_id,
                    j.title AS job_title,
                    a.applied_on,
                    a.status  -- Assuming you have a 'status' column in 'applications'
                FROM
                    applications a
                JOIN
                    jobs j ON a.job_id = j.id
                WHERE
                    a.user_id = :user_id
                ORDER BY
                    a.applied_on DESC
            """),
            {"user_id": user_id}
        )
        applications = [dict(row._mapping) for row in result.all()]
        return applications
    
def has_user_applied(job_id, user_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1 FROM applications WHERE job_id = :job_id AND user_id = :user_id"),
            {"job_id": job_id, "user_id": user_id}
        )
        return result.fetchone() is not None



def insert_job_to_db(title, location, salary, currency, responsibilities, requirements):
    connection = engine.connect()  # Assuming 'engine' is your SQLAlchemy engine
    try:
        query = text(
            "INSERT INTO jobs (title, location, salary, currency, responsibilities, requirements) "
            "VALUES (:title, :location, :salary, :currency, :responsibilities, :requirements)"
        )
        connection.execute(query, {
            "title": title,
            "location": location,
            "salary": salary,
            "currency": currency,
            "responsibilities": responsibilities,
            "requirements": requirements,
        })
        connection.commit()
        return True
    except Exception as e:
        print(f"Error inserting job: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def get_applications():
    with engine.connect() as connection:
         result = connection.execute(text("SELECT id, job_id, user_id, name, email, resumeurl, applied_date FROM applications")).fetchall()
         return [dict(row._mapping) for row in result]
    

def get_application_by_id(application_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM applications WHERE id = :application_id"),
            {"application_id": application_id}
        )
        application = result.fetchone()
        if application:
            return dict(application._mapping)  # Convert to dictionary
        return None
    
def get_recruiter_by_email(email):
    with engine.connect() as connection:
        result = result = connection.execute(text("SELECT id, username, email, password FROM recruiters WHERE email = :email"), {"email": "email"}).fetchone()
        jobs = result.all()
        return [dict(row._mapping) for row in jobs]  # Convert to list of dictionaries
    
def get_jobs_by_recruiter(recruiter_id):
   with engine.connect() as connection:
        result = connection.execute(text("SELECT id, title, location, salary, currency, responsibilities, requirements, posted_date FROM jobs WHERE recruiter_id = :recruiter_id"), {"recruiter_id": recruiter_id}).fetchall()
        return [dict(row._mapping) for row in result]
  