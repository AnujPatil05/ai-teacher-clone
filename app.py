from flask import Flask, render_template, request, jsonify, send_file, redirect
from chatbot import TeacherClone
from voice_clone_gtts import VoiceClonerGTTS
import os
import uuid

app = Flask(__name__)

print("🚀 Initializing Teacher Clone AI...")
try:
    teacher_clone = TeacherClone()
    print("✓ Chatbot loaded")
except Exception as e:
    print(f"✗ Chatbot failed: {e}")
    teacher_clone = None

try:
    voice_cloner = VoiceClonerGTTS()
    print("✓ Voice cloner loaded")
except Exception as e:
    print(f"✗ Voice cloner failed: {e}")
    voice_cloner = None

os.makedirs("static", exist_ok=True)

# Landing page route
@app.route('/')
def landing():
    return render_template('landing.html')

# Chat page route
@app.route('/chat')
def chat_page():
    return render_template('chat.html')

# Old route redirect
@app.route('/index')
def index():
    return redirect('/chat')

# Chat API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '')
        voice_enabled = data.get('voice', False)
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if teacher_clone:
            response_text = teacher_clone.get_response(question)
        else:
            response_text = "Teacher clone not initialized."
        
        result = {
            'response': response_text,
            'audio_url': None
        }
        
        if voice_enabled and voice_cloner:
            filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            output_path = f"static/{filename}"
            
            try:
                voice_cloner.generate_voice(response_text, output_path=output_path)
                result['audio_url'] = f'/audio/{filename}'
            except Exception as e:
                print(f"Voice generation failed: {e}")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/metrics')
def metrics():
    """Display evaluation metrics dashboard"""
    return render_template('metrics.html')

@app.route('/run_evaluation', methods=['POST'])
def run_evaluation():
    """Run evaluation and return results"""
    try:
        from evaluation import ChatbotEvaluator
        evaluator = ChatbotEvaluator()
        results = evaluator.run_test_suite()
        return jsonify(results['metrics'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500  
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('video')
        label = request.form.get('label', 'untitled')

        if file:
            filename = f"{label}_{file.filename}"
            save_path = os.path.join("uploads", filename)
            os.makedirs("uploads", exist_ok=True)
            file.save(save_path)
            return render_template("upload.html", status=f"✅ File saved: {filename}")
        else:
            return render_template("upload.html", status="❌ No file selected")

    return render_template("upload.html", status="")

@app.route('/audio/<filename>')
def serve_audio(filename):
    try:
        return send_file(f'static/{filename}', mimetype='audio/mpeg')
    except Exception as e:
        return "Audio not found", 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎓 Gate Smashers AI Clone Server")
    print("🎙️ Powered by Google TTS")
    print("="*50)
    print("📍 Landing Page: http://localhost:5000")
    print("📍 Chat Direct: http://localhost:5000/chat")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
