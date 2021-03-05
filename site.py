from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
import psycopg2
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()


# Kullanıcı Giriş Decaratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Bu sayfayı görüntülemek için giriş yapınız..", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = 'show_message'

DB_HOST = os.getenv('PSQL_URL')
DB_NAME = os.getenv('PSQL_DB')
DB_USER = os.getenv('PSQL_USER')
DB_PASS = os.getenv('PSQL_PASS')


#DB_URL = "postgresql://{}:5432{}@{}/{}".format(DB_USER, DB_PASS, DB_HOST, DB_NAME)
DB_URL = 'postgresql://postgres:murat123@localhost/et_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Form ile dosya yükleme işlemi
@app.route('/addfile', methods=['POST'])
def dosyayukle():

    if request.method == 'POST':

        # formdan dosya gelip gelmediğini kontrol edelim
        if 'image' not in request.files:
            flash('Dosya seçilmedi1')
            return redirect('addarticle')

        # kullanıcı dosya seçmemiş ve tarayıcı boş isim göndermiş mi
        image = request.files['image']
        if image.filename == '':
            flash('Dosya seçilmedi2')
            return redirect('addarticle')

        # gelen dosyayı güvenlik önlemlerinden geçir
        if image and allowed_file(image.filename):

            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            title = request.form.get('title')
            content = request.form.get('content')
            newArticle = Articles(title=title, content=content, image=filename)

            db.session.add(newArticle)
            db.session.commit()

            flash('Yazınız Başarıyla Eklendi :)', 'success')
            return redirect(url_for('dashboard', filename=filename))
            # return redirect('addarticle')
        else:

            flash('İzin verilmeyen dosya uzantısı')
            return redirect('addarticle')

    else:
        abort(401)


class LoginForm(Form):
    username = StringField("kullanıcı Adı")
    password = PasswordField("Parola")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/sevgili-terapist')
def terapist():
    return render_template("terapist.html")


@app.route("/bireysel-danışmanlık")
def bireysel():
    return render_template("bireysel.html")


@app.route('/aile-ve-çift-terapisi')
def aile():
    return render_template("aile.html")


@app.route('/emdr')
def emdr():
    return render_template("emdr.html")

@app.route('/atölye')
def atolye():
    return render_template("atolye.html")



@app.route('/çocuk-ergen-aile')
def cocuk():
    return render_template("cocuk.html")
@app.route('/online-terapi')
def online():
    return render_template("online.html")

@app.route("/article")
def article():
    articles = Articles.query.all()

    if articles:
        return render_template('article.html', articles=articles)

    return render_template("article.html")

# Yazı ekleme


@app.route("/addarticle", methods=["POST", "GET"])
@login_required
def addarticle():

    form = request.form
    if request.method == 'POST':

        return redirect(url_for('dashboard'))

    return render_template("addarticle.html", form=form)

# detay sayfası


@app.route("/articles/<string:id>")
def articles(id):

    article = Articles.query.all()

    if article:

        article = Articles.query.filter_by(id=id).first()

        return render_template("articles.html", article=article)
    else:
        return render_template("articles.html")

# yazı silme

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    article = Articles.query.all()
    
    
    if article:
        article = Articles.query.filter_by(id=id).first()
        db.session.delete(article)
        db.session.commit()
        
        return redirect(url_for("dashboard"))

    return render_template("dashboard.html", article=article)
# yazı güncelle


@app.route("/edit/<string:id>", methods=["GET", "POST"])
@login_required
def update(id):

    Articles.query.all()
    if request.method == "GET":

        article = Articles.query.filter_by(id=id).first()

        form = ArticleForm()
        form.title.data = article.title
        form.content.data = article.content

        return render_template("update.html", form=form)

    else:
        article = Articles.query.filter_by(id=id).first()
        form = ArticleForm(request.form)
        article.title = form.title.data
        article.content = form.content.data

        db.session.commit()
        flash("Yazınız güncenlendi...", "success")
        return redirect(url_for("dashboard"))


# Yazı Form sayfası

class ArticleForm(Form):
    title = StringField('Yazı Başlığı', [
        validators.DataRequired(message='required'),
        validators.Length(min=5, max=300)
    ])
    content = TextAreaField('Yazı içeriği', [validators.InputRequired(
        message='required'), validators.Length(min=10)])


@app.route("/dashboard")
@login_required
def dashboard():

    articles = Articles.query.all()

    if articles:
        return render_template('dashboard.html', articles=articles)

    else:
        return render_template("dashboard.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        usernamex = form.username.data
        passwordenter = form.password.data
        User.query.all()
        if User.query.filter_by(username=usernamex, password=passwordenter).first():

            session['logged_in'] = True
            session['username'] = usernamex
            flash('Başarı ile giriş yaptınız', 'success')

            return redirect(url_for('article'))

        else:
            flash('Kullanıcı adı veya parola yanlış', 'danger')
            return redirect(url_for('login'))

    else:
        return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


db.create_all()


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # (nullable=False) == (NOT NULL)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           nullable=False, default=datetime.now())


db.create_all()

if __name__ == "__main__":

    app.run(debug=True)
