from flask import Flask, request, render_template



app=Flask(__name__)

JOBS=[{
    'id':1,
    'title':'Software Engineer',
    'location':'Lagos',
    'salary':100000,
    'company':'Google'
},
{
    'id':2,
    'title':'Machine Learning Engineer',
    'location':'INDIA',
    'salary':120000,
    'company':'Nvidia'
},
{
    'id':3,
    'title':'Data Engineer',
    'location':'JAPAN',
    'salary':150000,
    'company':'Toyota'
}
]

@app.route('/')
def home():
    return render_template('home.html'
                           ,jobs=JOBS)


if __name__ == '__main__':
    app.run(debug=True)