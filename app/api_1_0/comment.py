from flask import jsonify, url_for, request, g
from . import api
from ..models import Comment, Post, Permit
from .. import db
from ..decorators import require_permit


@api.route('/comment/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    return jsonify(comment.to_json())


@api.route('/post/<int:post_id>/comments/')
def get_post_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'post': url_for('api.get_post', post_id=post_id, _external=True),
    })


@api.route('/post/<int:post_id>/comments/', methods=['POST'])
@require_permit(Permit.comment)
def write_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment(content=request.json.get('comment'))
    comment.post = post
    comment.author = g.current_user
    db.session.add(comment)
    db.session.commit()
    return jsonify({comment.to_json()}, 201,
                   {'Location': url_for('api.get_comment', comment_id=comment.id, _external=True)})
