from flask import Flask, render_template, make_response, url_for, session, redirect, request
import requests
from datetime import datetime, timedelta
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", password="Pass0101", database="NEWS")
mycursor = mydb.cursor()

current_time = datetime.utcnow()

app = Flask(__name__)
app.secret_key = "mykey"

def encode_password(password):
    encrpyt_password = ""
    for i in password:
        encrpyt_password += chr(ord(i)+1)
    return encrpyt_password[::-1]

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('Register.html')

@app.route('/register_user', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        phone_no = request.form.get('ph_number')
        user_name = request.form.get('login')
        password = request.form.get('pwd')
        confirm_password = request.form.get('c_pwd')      

        if password == confirm_password:
            confirm_password = encode_password(confirm_password)
            try:
                mycursor.execute("INSERT INTO USERINFO VALUES (%s, %s, %s, %s, %s)", (user_name, f_name, l_name, phone_no, confirm_password))
                mydb.commit()
                acknowledge_user((f_name+"your account has been created successfully"))
                return render_template('login.html')
            except Exception as e:                
                return render_template('Register.html')

@app.route('/home' , methods=['GET','POST'])
def login_user():
    if request.method == 'POST':
        user_name = request.form.get('login')
        password = request.form.get('pwd')
        password = encode_password(password)
        mycursor.execute("SELECT * FROM USERINFO WHERE user_name = %s AND user_password = %s", (user_name, password))
        user = mycursor.fetchone()
        if user:
            session['user_name'] = user[0]
            session['password'] = user[4]
            acknowledge_user(("Hi"+user[1]+" "+user[2]+" welcome to the news portal"));
            return redirect(url_for('index'))        
        else:
            acknowledge_user("Invalid Credentials")
            return render_template('login.html')


@app.route('/index')
def index():
    url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=e22f9dfe94e74b26a01b7d776944101c"
    req = requests.get(url).json()

    cases = {
        'articles' : req['articles']
    }
    li = [cases]

    headlines = ''

    for i in li[0]['articles']:
        headlines += i['title'] + " \t||\t "

    for i in li[0]['articles']:
        given_time = datetime.strptime(i['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        time_difference = current_time - given_time
        days = time_difference.days
        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds // 60) % 60
        if days == 0:
            if hours == 0:
                i['publishedAt'] = f"{minutes} minutes ago"
            else:
                i['publishedAt'] = f"{hours} hours ago"
        else:
            if days == 1:
                i['publishedAt'] = f"{days} day ago"
            else:
                i['publishedAt'] = f"{days} days ago"

    return render_template('index.html',news=li,user_name=session['user_name'],headlines=headlines)

@app.route('/category/<string:selected_category>')
@app.route('/category/category/<string:selected_category>')
def index_to_category(selected_category):
    category_name = "Business & Finance"
    category = "business"
    url =  "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=e22f9dfe94e74b26a01b7d776944101c"    
    if selected_category == 'b_f':
        category = "business"
        category_name = "Business & Finance"

    elif selected_category == 'tech':
        category = "technology"
        category_name = "Technology"
        
    elif selected_category == 'health':
        category = "health"
        category_name = "Health & Medicine"
        
    elif selected_category == 'sports':
        category = "sports"
        category_name = "Sports"
        
    elif selected_category == 'entertainment':
        category = "entertainment"
        category_name = "Entertainment"
        
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey=e22f9dfe94e74b26a01b7d776944101c"

    req = requests.get(url).json()
    category_news = {
        'articles' : req['articles']
    }

    for i in category_news['articles']:
        given_time = datetime.strptime(i['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        time_difference = current_time - given_time
        days = time_difference.days
        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds // 60) % 60
        if days == 0:
            if hours == 0:
                i['publishedAt'] = f"{minutes} minutes ago"
            else:
                i['publishedAt'] = f"{hours} hours ago"
        else:
            if days == 1:
                i['publishedAt'] = f"{days} day ago"
            else:
                i['publishedAt'] = f"{days} days ago"
    
    return render_template('category.html',category_news=category_news,category_name=category_name,user_name=session['user_name'])

@app.route('/search_result', methods=['GET','POST'])
def search_result():
    if request.method == 'POST':        
        search_query = request.form.get('s')        
        url = f"https://newsapi.org/v2/everything?q={search_query}&apiKey=e22f9dfe94e74b26a01b7d776944101c"
        req = requests.get(url).json()
        search_result = {
            'articles' : req['articles']
        }

        for i in search_result['articles']:
            given_time = datetime.strptime(i['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            time_difference = current_time - given_time
            days = time_difference.days
            hours = time_difference.seconds // 3600
            minutes = (time_difference.seconds // 60) % 60
            if days == 0:
                if hours == 0:
                    i['publishedAt'] = f"{minutes} minutes ago"
                else:
                    i['publishedAt'] = f"{hours} hours ago"
            else:
                if days == 1:
                    i['publishedAt'] = f"{days} day ago"
                else:
                    i['publishedAt'] = f"{days} days ago"

        return render_template('search_result.html',search_result=search_result,search_query=search_query,user_name=session['user_name'])

@app.route('/about')
def index_to_about():
    return render_template('about.html',user_name=session['user_name'])

@app.route('/contact')
def index_to_contact():
    return render_template('contact.html',user_name=session['user_name'])

@app.route('/submit-feedback', methods=['GET','POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form.get('cName')
        email = request.form.get('cEmail')
        website = request.form.get('cWebsite')
        message = request.form.get('cMessage')
        mycursor.execute("INSERT INTO feedback VALUES (%s, %s, %s, %s)", (name, email, website, message))
        mydb.commit()
        acknowledge_user("Thank you for your feedback")
        return render_template('contact.html',user_name=session['user_name'])

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    session.pop('password', None)
    acknowledge_user("You have been logged out successfully")
    return redirect(url_for('login'))

def acknowledge_user(user_name):
    from win32com.client import Dispatch
    speak = Dispatch("SAPI.SpVoice")
    speak.speak(user_name)


if __name__ == "__main__":
    app.run(debug=True)