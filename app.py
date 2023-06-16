from flask import Flask
from flask import render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import bcrypt
import functools


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Blog post.db"
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text,nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # email = db.Column(db.String(40), nullable=False)
    # password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return 'Blog post ' + str(self.id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String,nullable=False)
    password = db.Column(db.String(20), nullable=False, default='N/A')
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    
    
    def __repr__(self):
        return 'User ' + str(self.id)



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", posts=posts)


@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        login_user = User.query.filter_by(email=email).first()

        if login_user:
            print("user exits!")
            encrypt_password = bcrypt.hashpw(password.encode('utf-8'), login_user.password)
            if encrypt_password == login_user.password:
                print(f' {login_user.username}')
                session['username'] = login_user.username
                return redirect('/posts')  
        return '<h1>Invalid email/password combination!!</h1>'

    return render_template('login.html')


def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return func(*args, **kwargs)

    return secure_function

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    print(session)
    return render_template("login.html")


@app.route('/about')
def about():
    return '<h1>About Page</h1>'

@app.route('/base')
def base():
    return render_template("base.html", title='About') 

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    # if request.method == 'POST':
    #     post_title = request.form['title']
    #     post_author = request.form['author']
    #     post_content = request.form['content']
    #     new_post = BlogPost(title=post_title, content=post_content, author=post_author)
    #     db.session.add(new_post)
    #     db.session.commit()
    #     return redirect('/posts')
    # else:
    all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
    return render_template("posts.html", posts = all_posts)

# delete
@app.route('/posts/delete/<int:id>')
@login_required
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')

# edit
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post=post)

@app.route('/posts/add', methods=['GET', 'POST'])
@login_required
def new_post():
    
    if request.method == 'POST':
        post_title = request.form['title']
        post_author = request.form['author']
        post_content = request.form['content']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('new_post.html')


@app.route('/signup', methods=['GET', 'POST'])

def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user is None:
            encrypt_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # print(f'{username} + {email} + {encrypt_password}')
            new_user = User(username=username, email=email, password=encrypt_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        else:
            return f'<h1> {username} + already exists! </h1>'
    
    return render_template("signup.html") 



sd = User.query.all()
print(sd[0].password)


# def login_required(func):
#     @functools.wraps(func)
#     def secure_function(*args, **kwargs):
#         if "username" not in session:
#             return redirect("login.html")
#         return func(*args, **kwargs)

#     return secure_function


# @app.route('/logout')
# @login_required
# def logout():
#     session.pop('username', None)
#     print(session)
#     return render_template("login.html")



port = int(os.getenv('PORT', 8080))   
if __name__ == '__main__':
    app.secret_key = 'f31acc3999ec5cdd0fd00e79b205cfef'
    app.run(host='0.0.0.0', port=port)


# if __name__ == '__main__' : 
#     app.run()