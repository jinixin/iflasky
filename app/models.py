# coding=utf-8
from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from datetime import datetime
from hashlib import md5
from markdown import markdown
from bleach import linkify, clean as bhclean
from sqlalchemy import or_


class Permit(object):
    follow = 0x01
    comment = 0x02
    write_article = 0x04
    manage_comment = 0x08
    admin = 0x80


_roles = {
    'User': (Permit.follow | Permit.comment | Permit.write_article, True),
    'Assistant': (Permit.follow | Permit.comment | Permit.write_article | Permit.manage_comment, False),
    'Administrator': (0xff, False)
}


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permit = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False)
    user_list = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name  # 定义直接输出该类对象

    @classmethod
    def update_permit(cls):  # cls为类对象
        for role_name in _roles:
            role = cls.query.filter_by(name=role_name).first()
            if role is None:
                role = cls(name=role_name)
            role.permit = _roles[role_name][0]
            role.default = _roles[role_name][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    fans_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    idol_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(48))
    summary = db.Column(db.String(256))
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_list = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def content_change(target, content, oldvalue, initiator):
        allow_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                      'h1', 'h2', 'h3', 'h4', 'h5' 'p', 'img', 'hr', 'p']
        allow_attributes = ['href', 'src']
        target.content_html = linkify(
            bhclean(markdown(content, output_format='html'), tags=allow_tags, attributes=allow_attributes, strip=False))

    def to_json(self):
        post_json = {
            'url': url_for('api.get_post', post_id=self.id, _external=True),
            'title': self.title,
            'summary': self.summary,
            'content': self.content_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', user_id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', post_id=self.id, _external=True),
            'comments_count': self.comment_list.count(),
        }
        return post_json


db.event.listen(Post.content, 'set', Post.content_change)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.String(256))
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(64))
    about_me = db.Column(db.String(64))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    post_list = db.relationship('Post', backref='author', lazy='dynamic')  # lazy使user.post_list不会马上返回结果
    idol_list = db.relationship('Follow', foreign_keys=[Follow.fans_id], backref=db.backref('fans', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    fans_list = db.relationship('Follow', foreign_keys=[Follow.idol_id], backref=db.backref('idol', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    comment_list = db.relationship('Comment', backref='author', lazy='dynamic')
    send_list = db.relationship('Message', foreign_keys=[Message.sender_id],
                                backref=db.backref('sender', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    receive_list = db.relationship('Message', foreign_keys=[Message.receiver_id],
                                   backref=db.backref('receiver', lazy='joined'),
                                   lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)  # super(类名, self)==基类引用
        if self.role is None:
            if self.email == current_app.config['MAIL_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username

    @property  # 将该方法定义为属性，调用时无需加()
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def make_token(self, expire=3600):  # 产生令牌
        s = Serializer(current_app.config['SECRET_KEY'], expire)
        return s.dumps({'num': self.id})

    def check_confirm_token(self, token):  # 接受令牌并验证
        user_id = self.token2id(token)
        if user_id != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @classmethod
    def check_api_token(cls, token):  # 接受令牌并验证
        user_id = User.token2id(token)
        return User.query.get(user_id)

    @staticmethod
    def token2id(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return None
        return data.get('num')

    def check_permit(self, permit):
        return self.role is not None and self.role.permit & permit == permit

    def is_administrator(self):
        return self.check_permit(Permit.admin)

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def make_gravatar_url(self, size=80, kind='retro'):
        if self.avatar_hash is None:
            self.avatar_hash = md5(self.email.encode('utf-8')).hexdigest()
            db.session.add(self)
        url = 'http://www.gravatar.com/avatar'
        return '%s/%s?s=%s&d=%s' % (url, self.avatar_hash, size, kind)

    def is_following(self, user):  # 是否关注user
        return self.idol_list.filter_by(idol_id=user.id).first() is not None

    def is_followed_by(self, user):  # 是否被user关注，感觉该方法功能上与is_following重复
        return self.fans_list.filter_by(fans_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            db.session.add(Follow(fans=self, idol=user))

    def unfollow(self, user):
        record = self.idol_list.filter_by(idol_id=user.id).first()
        if record is not None:
            db.session.delete(record)

    def show_idols_article_sql(self):
        return Post.query.join(Follow, Follow.idol_id == Post.author_id).filter(
            or_(self.id == Follow.fans_id, self.id == Post.author_id))  # 或关系

    def to_json(self):
        user_json = {
            'url': url_for('api.get_user', user_id=self.id, _external=True),
            'email': self.email,
            'username': self.username,
            'posts': url_for('api.get_user_posts', user_id=self.id, _external=True),
            'posts_count': self.post_list.count(),
        }
        return user_json


class AnonymousUser(AnonymousUserMixin):
    def check_permit(self, permit):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    closed = db.Column(db.Boolean, default=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_json(self):
        comment_json = {
            'url': url_for('api.get_comment', comment_id=self.id, _external=True),
            'content': self.content,
            'timestamp': self.timestamp,
            'closed': self.closed,
            'post': url_for('api.get_post', post_id=self.post_id, _external=True),
            'author': url_for('api.get_user', user_id=self.author_id, _external=True),
        }
        return comment_json
