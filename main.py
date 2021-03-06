# flask framework
from flask import Flask, render_template, request, make_response, session, redirect, abort, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import reqparse, abort, Api, Resource

# models
from data import db_session, news_resources
from data.users import User
from data.news import News
from data import  news_api

# forms
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from forms.news_form import NewsForm

# extra modules
import datetime

# flask init
app = Flask(__name__)
api = Api(app)

app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# login manager init
login_manager = LoginManager()
login_manager.init_app(app)


from flask import make_response

@app.errorhandler(404)
def not_found(error):
    """This page means that user query isn't correct"""
    return make_response(jsonify({'error': 'Not found'}), 404)

@login_manager.user_loader
def load_user(user_id):
    """"Get user with user_id"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def home_page():
    """"Home page (/) show all current user news and all public news"""
    db_sess = db_session.create_session()
    # news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister_page():
    """"Register user with Register Form
    Fields: name, email, about, password"""
    form = RegisterForm()
    # register button
    if form.validate_on_submit():
        # check password match
        if form.password.data != form.password_again.data:
            # passwords isn't match
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="???????????? ???? ??????????????????")
        # new session
        db_sess = db_session.create_session()
        # check registered
        if db_sess.query(User).filter(User.email == form.email.data).first():
            # this email was registered
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="?????????? ???????????????????????? ?????? ????????")
        # user data
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='??????????????????????', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """"Login using email and password
    Check correctness login and password
    After that, redirect to home(/) """
    # login form
    form = LoginForm()

    # submit button
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # user search
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # check password
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # go home
            return redirect("/")

        # user error
        return render_template('login.html',
                               message="???????????????????????? ?????????? ?????? ????????????",
                               form=form)
    # return template
    return render_template('login.html', title='??????????????????????', form=form)


@app.route('/logout')
@login_required
def logout_page():
    """"Logout page
    kill current user session and redirect to home(/)"""
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news_page():
    """"Add news( available only for users)
    Create form: title, content, is_private (created date and user id automatically)
    After submit redirect to home"""

    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect('/')
    return render_template('news.html', title='???????????????????? ??????????????',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news_page(id):
    """"Edit an exsisting news( only for the creator of this news)
    Editing fields: title, content, is_private
    (Created date does not change)
    After submit redirect to home"""
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='???????????????????????????? ??????????????',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete_page(id):
    """"delete an exsisting news( only for the creator of this news)
        After submit redirect to home"""
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')





def main():
    db_session.global_init("db/blogs.db")
    # app.register_blueprint(news_api.blueprint)

    # ?????? ???????????? ????????????????
    api.add_resource(news_resources.NewsListResource, '/api/v2/news')

    # ?????? ???????????? ??????????????
    api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')

    app.run(port='8080')


if __name__ == '__main__':
    main()
