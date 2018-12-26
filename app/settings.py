import os

PER_PAGE = 10
UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
MOVIE_DIR = 'movie'
PREVIEW_DIR = 'preview'
AVATAR_DIR = 'avatar'
MOVIE_PATH = os.path.join(UP_DIR, MOVIE_DIR)
PREVIEW_PATH = os.path.join(UP_DIR, PREVIEW_DIR)
AVATAR_PATH = os.path.join(UP_DIR, AVATAR_DIR)

