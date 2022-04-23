from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    icon_path = db.Column(db.String(120))
    admin = db.Column(db.Boolean, default=False)
    root = db.Column(db.Boolean, default=False)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        if self.icon_path is None:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        else:
            return self.icon_path

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# ----------------------------------------------------------------------------


class Spoiler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    link = db.Column(db.String(2048))


class LatestRecommend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class J2Recommend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class ProgrammeRecommend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class LatestNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    title = db.Column(db.String(64))
    link = db.Column(db.String(2048))
    date = db.Column(db.DateTime, index=True)


class EntertainmentNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    title = db.Column(db.String(64))
    link = db.Column(db.String(2048))
    date = db.Column(db.DateTime, index=True)


class myTVSUPER(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class bigbigshop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class DigitalContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class SpoilersBar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))

# -------------------------- Footer ------------------------------------------


class RelatedLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    link = db.Column(db.String(2048))


class AboutUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    link = db.Column(db.String(2048))


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))


class FollowUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(128))
    link = db.Column(db.String(2048))

# ------------------------------ Programme -----------------------------------


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    image = db.Column(db.String(128))

    def avatar(self, size):
        if self.image is None:
            digest = md5(self.name.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        else:
            return self.image


class ProgrammeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    station = db.Column(db.String(10), db.ForeignKey('station.id'), nullable=False)
    station_ref = db.relationship('Station', backref=db.backref('ProgrammeList_ref', lazy='dynamic'))
    time = db.Column(db.DateTime, index=True)


class Programme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    station = db.Column(db.String(10), db.ForeignKey('station.id'), nullable=False)
    station_ref = db.relationship('Station', backref=db.backref('Programme_ref', lazy='dynamic'))
    image = db.Column(db.String(128))


class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False)
    author_ref = db.relationship('User', backref=db.backref('ForumPost_ref1', lazy='dynamic'))
    programme = db.Column(db.String(10), db.ForeignKey('programme.id'), nullable=False)
    programme_ref = db.relationship('Programme', backref=db.backref('ForumPost_ref2', lazy='dynamic'))
    title = db.Column(db.String(32), unique=True)
    body = db.Column(db.String(512))
    date = db.Column(db.DateTime, index=True)


class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    post_ref = db.relationship('ForumPost', backref=db.backref('ForumReply_ref1', lazy='dynamic'))
    author = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False)
    author_ref = db.relationship('User', backref=db.backref('ForumReply_ref2', lazy='dynamic'))
    body = db.Column(db.String(512))
    date = db.Column(db.DateTime, index=True)


class UploadFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(32), unique=True)