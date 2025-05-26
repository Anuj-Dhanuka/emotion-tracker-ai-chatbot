import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import uuid

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mood_journal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Load environment variables
load_dotenv()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    messages = db.relationship('Message', backref='conversation', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    text = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(20))
    color = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def analyze_emotion(text):
    """Analyze text and return emotion and color"""
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze the following text and return the primary emotion in one word (happy, sad, angry, anxious, excited).
        Text: {text}
        Emotion: """
        
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()
        
        # Map emotions to colors
        color_map = {
            'happy': '#FFD700',
            'excited': '#FFA500',
            'sad': '#ADD8E6',
            'angry': '#FF4500',
            'anxious': '#FFB6C1'
        }
        
        return emotion, color_map.get(emotion, '#FFFFFF')
    except Exception as e:
        print(f"Error analyzing emotion: {str(e)}")
        return 'unknown', '#FFFFFF'

def generate_response(text, emotion):
    """Generate an empathetic response based on emotion"""
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Generate a short, warm, and caring response to someone feeling {emotion}.
        Their text: {text}
        Response: """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I'm here for you. How can I help you today?"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        text = data.get('text', '')
        conversation_id = data.get('conversation_id')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Get or create conversation
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
            if not conversation:
                return jsonify({'error': 'Invalid conversation ID'}), 400
        else:
            conversation = Conversation(user_id=str(uuid.uuid4()))
            db.session.add(conversation)
            db.session.commit()
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role='user',
            text=text
        )
        db.session.add(user_message)
        
        # Get conversation history
        messages = Message.query.filter_by(conversation_id=conversation.id).all()
        
        # Create context for AI response
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.text
            })
        
        # Generate AI response
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Analyze emotion
        emotion, color = analyze_emotion(text)
        
        # Format context as a single string
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
        
        # Generate response with context
        response = model.generate_content([
            {
                "role": "user",
                "parts": [{"text": context_str}]
            }
        ],
        generation_config={
            "temperature": 0.7
        })
        response_text = response.text.strip()
        
        # Save AI message
        ai_message = Message(
            conversation_id=conversation.id,
            role='ai',
            text=response_text,
            emotion=emotion,
            color=color
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'conversation_id': conversation.id,
            'emotion': emotion,
            'color': color,
            'response': response_text
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': 'Failed to process message'
        }), 500

@app.route('/mood_history')
def mood_history():
    # Get the latest messages with emotions
    messages = Message.query.filter(
        Message.emotion.isnot(None)
    ).order_by(Message.timestamp.desc()).limit(7).all()
    
    return jsonify([{
        'date': msg.timestamp.strftime('%Y-%m-%d'),
        'emotion': msg.emotion,
        'color': msg.color
    } for msg in messages])

if __name__ == '__main__':
    app.run(debug=True)
