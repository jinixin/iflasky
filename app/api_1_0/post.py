from flask import jsonify, url_for, request, g
from . import api
from ..models import Post, Permit
from .. import db
from ..decorators import require_api_permit
from .errors import forbidden


@api.route('/post/<int:post_id>')
def get_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    return jsonify(post.to_json())


@api.route('/post/<int:post_id>', methods=['PUT'])
@require_api_permit(Permit.write_article)
def update_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if g.current_user != post.author and not g.current_user.is_administrator():
        return forbidden()
    raw = request.json
    post.title = raw.get('title', post.title)
    post.summary = raw.get('summary', post.summary)
    post.content = raw.get('content', post.content)
    db.session.add(post)
    return jsonify(post.to_json())


@api.route('/post/')
def get_all_posts():
    posts = Post.query.all()
    return jsonify({
        'posts': [post.to_json() for post in posts]
    })


@api.route('/post/', methods=['POST'])
@require_api_permit(Permit.write_article)
def write_article():
    raw = request.json
    title = raw.get('title')
    summary = raw.get('summary')
    content = raw.get('content')
    post = Post(title=title, summary=summary, content=content)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', post_id=post.id, _external=True)}


@api.route('/user/<int:user_id>/posts/')
def get_user_posts(user_id):
    posts = Post.query.filter_by(author_id=user_id).all()
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'author': url_for('api.get_user', user_id=user_id, _external=True),
    })
