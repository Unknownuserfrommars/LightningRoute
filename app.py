# app.py - Flask 后端

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 导入自定义模块
from extract import GPTProcessor
from graph import GraphGenerator

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route("/")
def home():
    return "Flask is running on Render!"

@app.route("/api/generate-map", methods=["POST"])
def generate_map():
    # 调试信息，帮助确认路由是否被调用
    print("✅ /api/generate-map endpoint called")
    
    data = request.json
    text = data.get("text", "")
    
    if not text:
        print("❌ No text provided in request")
        return jsonify({"error": "No text provided"}), 400

    try:
        # 使用 GPTProcessor 从文本中提取知识点
        gpt_processor = GPTProcessor()
        knowledge_points = gpt_processor.extract_knowledge(text)
        print("✅ Knowledge points extracted:", knowledge_points)
        
        # 使用 GraphGenerator 生成思维导图数据
        graph_generator = GraphGenerator()
        graph_data = graph_generator.generate_graph(knowledge_points)
        print("✅ Graph generated successfully")
        
        return jsonify(graph_data)
    except Exception as e:
        print(f"❌ Error in generate_map: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 环境一般传 PORT=5000
    print(f"🚀 Flask API is running on port {port}")
    app.run(host="0.0.0.0", port=port)
