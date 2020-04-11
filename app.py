from flask import Flask, render_template, redirect, url_for,flash,request
from flask_login import current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import InputRequired, Email, Length,ValidationError
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


# books =  [
#     {
#         'book': 'Microeconomics',
#         'author':'Manisha',
#         'publications':'Svnit publications'
#     },
#     {
#         'book': 'Finance',
#         'author':'Sunita',
#         'publications':'Kalyan publications'
#     }
# ]





app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {'books':'sqlite:///library.db','cart':'sqlite:///history.db'}
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    phone=db.Column(db.Integer,unique=True)


class Books(db.Model):
    __bind_key__ ='books'
    __searchable__=['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    author = db.Column(db.String(20))
    publications = db.Column(db.String(30))
    year=db.Column(db.Integer)
    isbn=db.Column(db.Integer)
    quantity=db.Column(db.Integer)
    cart = db.relationship("Cart", backref="name")    

class Cart(db.Model):
    __bind_key__='cart'
    id=db.Column(db.Integer,primary_key=True)
    issue_date=db.Column(db.DateTime)
    Books_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    phone = StringField('Phone',validators=[InputRequired(),Length(min=8,max=12)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('Email', validators=[InputRequired(),Email(message='Invalid email'), Length(max=50)])
    phone = StringField('Phone',validators=[InputRequired(),Length(min=8,max=12)])
    submit=SubmitField('Update')
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone number is taken. Please choose a different one.')
class InsertForm(FlaskForm):
    title=StringField('Title',validators=[InputRequired(),Length(max=30)])
    author=StringField('Author',validators=[InputRequired(),Length(max=30)])
    publications=StringField('Publications',validators=[InputRequired(),Length(max=30)])
    year=StringField('Year',validators=[InputRequired(),Length(max=5)])
    isbn=StringField('ISBN Number',validators=[InputRequired(),Length(max=30)])
    quantity=StringField('Quantity',validators=[InputRequired(),Length(max=10)])


class SearchForm(FlaskForm):
    search = StringField('search', [InputRequired()])
    submit = SubmitField('Search',
                       render_kw={'class': 'btn btn-success btn-block'})
    #issue = SelectField('issue',choices=[('Available','Available'),('Issued','Issued')])
    





   

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data,phone=form.phone.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/book/new',methods=['GET','POST'])
@login_required
def new_book():
    form=InsertForm()
    if form.validate_on_submit():
        add=Books(title=form.title.data,author=form.author.data,publications=form.publications.data,year=form.year.data,isbn=form.isbn.data,quantity=form.quantity.data)
        db.session.add(add)
        db.session.commit()
        flash('Your book has been added successfully','success')
        return redirect(url_for('new_book'))
    return render_template('insert_book.html',title='New Book',form=form)

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form=SearchForm()
    if request.method=='POST':
        update=Books.query.filter_by(id=Books.id.data).update(dict(quantity=Books.quantity-1))
        db.session.commit()
    return render_template('dashboard.html',form=form, name=current_user.username,query=Books.query.all(),search=form.search.data)

# @pp.route('/cart',methods=['POST'])
# def AddToCart():
#     try:
#         pass
#     except expression as identifier:
#         pass
#     else:
#         pass
#     finally:
#         pass


@app.route('/history')
@login_required
def history():
    book=Books.query.all()
    return render_template('history.html', name=current_user.username,book=book)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/profile',methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccount()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.email=form.email.data
        current_user.phone=form.phone.data
        db.session.commit()
        flash('your account has been updated','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
        form.phone.data=current_user.phone
    return render_template('profile.html',form=form)
# @app.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
