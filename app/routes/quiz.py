import json
import random
from flask import Blueprint, jsonify, request

quiz_bp = Blueprint('quiz', __name__)

# Load câu hỏi từ file
with open('app/static/quiz_data_1.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

@quiz_bp.route('/quiz/start', methods=['GET'])
def start_quiz():
    shuffled = quiz_data.copy()
    random.shuffle(shuffled)
    questions = []
    for q in shuffled:
        questions.append({
            'question': q['question'],
            'options': q['options']
        })
    return jsonify({'quiz': questions})


@quiz_bp.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    user_answers = data.get('answers')

    score = 0
    total = len(quiz_data)
    
    for idx, question in enumerate(quiz_data):
        correct = question['answer']
        user_answer = user_answers.get(str(idx))
        if user_answer == correct:
            score += 1

    final_score = round((score / total) * 10, 2)
    return jsonify({'score': final_score})
