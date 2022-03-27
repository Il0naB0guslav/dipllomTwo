from flask import Flask, render_template,request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
import json_fix
from flask_mail import Mail, Message
from flask.helpers import url_for

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'memcached'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'test@gmail.com'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = 'test@gmail.com'  # и здесь
app.config['MAIL_PASSWORD'] = 'password'  # введите пароль
mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    height = db.Column(db.Integer)
    years = db.Column(db.Integer)
    hair = db.Column(db.String(100))
    eyes = db.Column(db.String(100))
    activityType = db.Column(db.String(100))
    sex = db.Column(db.String(100))
    img = db.Column(db.String(500))

    def __repr__(self):
            return 'Article %r' % self.id
    def __json__(self):
        return {
          "id": self.id,
          "name": self.name,
          "height": self.height,
          "years": self.years,
          "hair": self.hair,
          "eyes": self.eyes,
          "img": self.img
        }


class Collection(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    img1 = db.Column(db.String(500))
    img2 = db.Column(db.String(500))
    img3 = db.Column(db.String(500))
    img4 = db.Column(db.String(500))
    img5 = db.Column(db.String(500))

    def __repr__(self):
            return 'Article %r' % self.id

class EmailQuestion(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    text = db.Column(db.Text)

    def __repr__(self):
            return 'Article %r' % self.id


class Galery(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    path = db.Column(db.String(500))
    type = db.Column(db.String(100))

    def __repr__(self):
            return 'Article %r' % self.id

class Achievements(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    text = db.Column(db.Text)
    path = db.Column(db.String(500))

    def __repr__(self):
            return 'Article %r' % self.id


def logged_in():
    # в сессии будет храниться информация о том, что пользователь вошёл
    return session.get('logged')

# от этого класса должны наследоваться все классы админки - кроме индекса
class MyView(BaseView):
    def is_accessible(self):
        return logged_in()

    def _handle_view(self, name, **kwargs):
        if not logged_in():
            # делать редирект в некоторых случаях не стоит
            return self.render('admin/login.html')


class AdminIndex(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        emailQuest = EmailQuestion.query.all()
        if request.method == 'POST':
            frm = request.form.get
            login = frm('login')
            password = frm('password')            

            # проверяете введённые данные...
            if login=='admin' and password=="1234":
                session.update({'logged':True})
                session.modified = True
                return self.render('admin/dashboard_index.html',emailQuest=emailQuest)
            else:
                return self.render('admin/login.html',error=u'Ошиблись паролем?..')
        # уже вошёл, но перешёл на /admin/
        if logged_in():
            return self.render('admin/login.html')
        return self.render('admin/login.html')

admin = Admin(app, template_mode='bootstrap3',index_view = AdminIndex())
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Collection, db.session))
admin.add_view(ModelView(Galery, db.session))
admin.add_view(ModelView(EmailQuestion, db.session))
admin.add_view(ModelView(Achievements, db.session))

@app.route('/')
def index():
    achievements = Achievements.query.all()
    return render_template("index.html",achievements=achievements)

@app.route('/collection_info/<int:id>')
def collection_info(id):
    collection = Collection.query.get(id)
    return render_template("collection_info.html", collection=collection)

@app.route('/collection')
def collection():
    collection = Collection.query.all()
    return render_template("collection.html",collection=collection)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        questtion = request.form.get('questtion')
        email_quest = EmailQuestion(name=name,email=email,text=questtion)
        try:
            db.session.add(email_quest)
            db.session.commit()
            return redirect ("/contact")
        except:
            return "Произошла ошибка!"
    return render_template("contact.html")

@app.route('/galery')
def galery():
    galery = Galery.query.all()
    return render_template("galery.html",galery=galery)

@app.route('/information/<int:id>')
def information(id):
    user = User.query.get(id)
    users = User.query.all()
    selectedUserIndex = users.index(user)
    return render_template("information.html",user=user,users=users, selectedUserIndex=selectedUserIndex)

@app.route('/users')
def users():
    user = User.query.all()
    return render_template("users.html",user=user)

@app.route('/email_send', methods=['GET', 'POST'])
def email_send():
    if request.method == 'POST':
        email_user = request.form.get('email_user')
        message = request.form.get('message')
        msg = Message("МАЛАДОСЦЬ", recipients=[email_user])
        msg.body = message
        mail.send(msg)
        return redirect("/admin")
    return redirect('/admin')

@app.route('/videos_filter', methods=['GET', 'POST'])
def videos_filter():
    if request.method == 'POST':
        galery = Galery.query.filter_by(type="video").all()
        return render_template("galery.html",galery=galery)
    return redirect('/galery')


@app.route('/images_filter', methods=['GET', 'POST'])
def images_filter():
    if request.method == 'POST':
        galery = Galery.query.filter_by(type="photo").all()
        return render_template("galery.html",galery=galery)
    return redirect('/galery')
    
if __name__=="__main__":
    app.run(debug=True)