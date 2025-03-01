# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from extract import GPTProcessor
from graph import GraphGenerator
import os
from flask import Flask

app = Flask(__name__)
CORS(app)

gpt_processor = GPTProcessor()
graph_generator = GraphGenerator()

@app.route('/api/process', methods=['POST'])
def process_text():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Extract knowledge points using GPT-4
        knowledge_points = gpt_processor.extract_knowledge(text)
        
        # Generate graph structure
        graph_data = graph_generator.generate_graph(knowledge_points)
        
        return jsonify({
            'success': True,
            'graph': graph_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is running on Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 读取 PORT 环境变量
    app.run(host="0.0.0.0", port=port)
