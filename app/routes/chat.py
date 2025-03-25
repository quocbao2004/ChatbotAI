import difflib
import json
from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)

with open('app/static/chat_rules.json', 'r', encoding='utf-8') as f:
    qa_data = json.load(f)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_q = request.json.get('question')
    threshold = 0.5
    best_match = None
    best_score = 0

    for qa in qa_data:
        score = difflib.SequenceMatcher(None, user_q.lower(), qa['question'].lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = qa

    if best_score >= threshold:
        return jsonify({
            'question': user_q,
            'answer': best_match['answer']
        })
    else:
        return jsonify({
            'question': user_q,
            'answer': "Xin lỗi, tôi chưa có thông tin về câu hỏi này."
        })
