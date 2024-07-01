from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy import desc
from pytz import timezone, utc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://Vadim:sPDM8KrN@localhost:3306/magic_ball_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'init_command': 'SET time_zone = "+03:00"'}
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

forbidden_words = [
    "фиолетовая утка", "фиолетовые утки", "фиолетовой утке", "фиолетовую утку", "фиолетовой уткой", "фиолетовою уткою", "фиолетовой утке", "фиолетовой утки", "фиолетовых уток", "фиолетовым уткам", 
    "фиолетовых утках", "фиолетовыми утками", "фиолетовых утках", 
    "фиолетовая улитка", "фиолетовые улитки", "фиолетовой улитке", "фиолетовую улитку", "фиолетовой улиткой", "фиолетовою улиткою", "фиолетовой улитке", "фиолетовой улитки", 
    "фиолетовый улиток", "фиолетовым улитка", "фиолетовых улитках", "фиолетовыми улитками", "фиолетовых улитках", "purple duck", "purple snail"
    ]

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def load_answers(answer_file):
    with open(answer_file, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/answer', methods=['POST'])
def get_answer():
    question = request.form.get('question')
    if not question:
        return render_template('answer.html', answer="Please enter a question.")
    
    for word in forbidden_words:
        if word in question.lower():
            return render_template('answer.html', answer="Вы ввели запрещенный запрос.")
    
    answers_file_path = 'C:/VScode/answers/answer.txt'
    answer_list = load_answers(answers_file_path)
    selected_answer = random.choice(answer_list)

    

    new_question = Question(question=question, answer=selected_answer)
    db.session.add(new_question)
    db.session.commit()

    return render_template('answer.html', question=question, answer=selected_answer)
    





@app.route('/admin')
def admin():
    try:
        questions = Question.query.order_by(desc(Question.timestamp)).all()
        eastern = timezone('Europe/Kiev')  
        for question in questions:
            question.timestamp = question.timestamp.replace(tzinfo=utc).astimezone(eastern)
        return render_template('admin.html', questions=questions)
    except OperationalError as e:
        error_msg = f"Error accessing database: {str(e)}"
        return render_template('admin.html', error=error_msg)
    

app.teardown_appcontext
def shutdown_session(expection=None):
    db.session.remove()
    
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except OperationalError as e:
            print(f"Error creating database tables: {str(e)}")
    app.run(debug=True)
