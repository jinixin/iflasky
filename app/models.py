# coding=utf-8
from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


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


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)  # super(类名, self)==基类引用
        print 'ggggg'
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def make_confirm_token(self, over_time=3600):
        s = Serializer(current_app.config['SECRET_KEY'], over_time)
        return s.dumps({'num': self.id})

    def check_token(self, token):
        user_id = self.token2id(token)
        if user_id != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

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


class AnonymousUser(AnonymousUserMixin):
    def check_permit(self, permit):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
