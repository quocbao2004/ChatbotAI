import json
import random
import os
from flask import Blueprint, jsonify, request
from flask_cors import CORS

quiz_bp = Blueprint('quiz', __name__)
CORS(quiz_bp)

# Load câu hỏi từ file
with open('app/static/quizzes/quiz_data_1.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

@quiz_bp.route('/quiz/list', methods=['GET'])
def list_quizzes():
    QUIZ_DIR = 'app/static/quizzes'  # thư mục chứa nhiều file .json
    quiz_files = [f for f in os.listdir(QUIZ_DIR) if f.endswith('.json')]
    quizzes = []

    for file in quiz_files:
        with open(os.path.join(QUIZ_DIR, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            quizzes.append({
                'id': file.replace('.json', ''),
                'title': data.get('title', 'No Title')
            })

    return jsonify({'quizzes': quizzes})

@quiz_bp.route('/quiz/<quiz_id>/start', methods=['GET'])
def start_quiz(quiz_id):
    QUIZ_DIR = 'app/static/quizzes'  
    quiz_file = os.path.join(QUIZ_DIR, f'{quiz_id}.json')
    with open(quiz_file, 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)

    shuffled_questions = quiz_data['questions'].copy()
    random.shuffle(shuffled_questions)

    questions = [{
        'question': q['question'],
        'options': q['options'],
        # không gửi đáp án đúng về client
    } for q in shuffled_questions]

    return jsonify({'quiz': questions})

@quiz_bp.route('/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    data = request.get_json()
    user_answers = data.get('answers', {})
    QUIZ_DIR = 'app/static/quizzes'  
    quiz_file = os.path.join(QUIZ_DIR, f'{quiz_id}.json')
    with open(quiz_file, 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)['questions']

    correct_count = sum(1 for idx, question in enumerate(quiz_data)
                        if user_answers.get(str(idx)) == question['answer'])

    total = len(quiz_data)
    final_score = round((correct_count / total) * 10, 2)

    return jsonify({'score': final_score})
