from flask import Blueprint, render_template

forum = Blueprint('forum', __name__)

@forum.route('/')
def index():
    return render_template('forum/index.html')
