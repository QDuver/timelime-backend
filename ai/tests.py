from ai import generate_timeline
from models.user import User
from routes.quizzes import create_quiz_
from routes.timelines import create_ai_timeline_, create_new_timeline
from utils.utils import set_env_variables
import firestore.firestore_init as firestore_init
import flask
from firestore.firestore_db import UnprotectedFirestoreDB


def main():
    set_env_variables()
    firestore_init.init()
    timelines = ['Napoleon III', 'Morocco', 'Decolonisation', 'Brasil', 'Star Trek', 'Python', 'Star Wars', 'Humanity', 'Solar System', 'World War II', 'World War I', 'Cold War', 'French Revolution', 'American Revolution',
    'Dinosaurs', 'Jesus', 'Ancient Egypt', 'Ancient Greece', 'Ancient Rome', 'Middle Ages', 'Renaissance', 'Industrial Revolution', 'French Empire', 'British Empire', 'Spanish Empire', 'Portuguese Empire', 'Russian Empire']
    for timeline in timelines:
        timeline = create_ai_timeline_(timeline, 50, False, test=True)
        quiz = create_quiz_(timeline['id'], test=True)
    # print(df)