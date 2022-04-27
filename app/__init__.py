import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app, redirect, url_for, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_wtf import FlaskForm
from sqlalchemy.dialects.mssql.information_schema import columns
from werkzeug.utils import secure_filename
from wtforms import StringField, form, FileField
from wtforms.validators import DataRequired

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
admin = Admin()

import app.globalvar
from app.models import *


# 全局
def global_var():
    # 入Data
    login_msg = login.login_message

    spoilers = Spoiler.query.all()
    related_links = RelatedLink.query.all()
    about_us = AboutUs.query.all()
    applications = Application.query.all()
    follow_us = FollowUs.query.all()

    latest_posts = ForumPost.query.order_by(ForumPost.date.desc()).limit(10).all()

    return dict(login_msg=login_msg,
                spoilers=spoilers,
                related_links=related_links,
                about_us=about_us,
                applications=applications,
                follow_us=follow_us,
                latest_posts=latest_posts)


class AdminModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False

    def is_accessible(self):
        if current_user.is_authenticated:
            user = User.query.filter_by(username=current_user.username).first()
            return user.admin
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index'))


class RootModelView(AdminModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            user = User.query.filter_by(username=current_user.username).first()
            return user.root
        else:
            return False


class UploadForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    filename = StringField('File Name (/static/upload/...)', validators=[DataRequired()])


class UploadView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    form = UploadForm

    def on_model_change(self, form, model, is_created):
        file = request.files[form.file.name]
        filename = form.filename.data
        file.save(os.path.join(current_app.config['UPLOAD_DATA'], filename))

    def on_model_delete(self, model):
        try:
            os.remove(current_app.config['UPLOAD_DATA'] + model.filename)
        except Exception as err:
            flash('Delete file failed!')


    def is_accessible(self):
        if current_user.is_authenticated:
            user = User.query.filter_by(username=current_user.username).first()
            return user.admin
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index'))


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    app.context_processor(global_var)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    admin.init_app(app)

    admin.add_view(RootModelView(User, db.session))

    admin.add_view(UploadView(UploadFile, db.session))
    basedir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(basedir + "/static/upload"):
        os.makedirs(basedir + "/static/upload")
    if not os.path.exists(basedir + "/static/usericon"):
        os.makedirs(basedir + "/static/usericon")

    admin.add_view(AdminModelView(Spoiler, db.session))
    admin.add_view(AdminModelView(SpoilersBar, db.session))

    admin.add_view(AdminModelView(Station, db.session))
    admin.add_view(AdminModelView(ProgrammeList, db.session))

    admin.add_view(AdminModelView(LatestRecommend, db.session))
    admin.add_view(AdminModelView(J2Recommend, db.session))
    admin.add_view(AdminModelView(ProgrammeRecommend, db.session))
    admin.add_view(AdminModelView(LatestNews, db.session))
    admin.add_view(AdminModelView(EntertainmentNews, db.session))
    admin.add_view(AdminModelView(myTVSUPER, db.session))
    admin.add_view(AdminModelView(bigbigshop, db.session))
    admin.add_view(AdminModelView(DigitalContent, db.session))

    admin.add_view(AdminModelView(RelatedLink, db.session))
    admin.add_view(AdminModelView(AboutUs, db.session))
    admin.add_view(AdminModelView(Application, db.session))
    admin.add_view(AdminModelView(FollowUs, db.session))

    admin.add_view(AdminModelView(Programme, db.session))

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/tvb.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
