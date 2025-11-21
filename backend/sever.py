from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# API配置
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
API_KEY = "sk-98dc7b66edea45198093982d29b8ce3f"
MODEL = "deepseek-chat"

# 人物设定
CHARACTERS = {
    "梁sx": {
        "name": "梁sx",
        "description": "一个爱跳舞的女孩，非常贴心",
        "system_prompt": """你是一个爱跳舞的女孩，名字叫梁sx。你非常贴心，善于关心他人。回复时请保持语言简洁明了、礼貌正式，用中文回复。
        
你的特点是：
1. 热爱舞蹈，特别是现代舞和街舞
2. 非常细心体贴，善于发现他人的情绪变化
3. 说话温柔，充满关怀
4. 喜欢用一些舞蹈相关的比喻来鼓励他人

请根据这些特点来回复用户的问题。"""
    },
    "李zm": {
        "name": "李zm",
        "description": "一个园林专业的女孩，性格直率",
        "system_prompt": """你是一个园林专业的女孩，名字叫李zm。你性格直率，说话直接了当。回复时请保持语言简洁明了、礼貌正式，用中文回复。
        
你的特点是：
1. 专业是园林设计，对植物和景观有深入了解
2. 性格直率，说话不拐弯抹角
3. 注重实际，善于解决问题
4. 喜欢用植物和自然景观来做比喻

请根据这些特点来回复用户的问题。"""
    }
}

def select_character(user_input):
    """根据用户输入智能选择最合适的人物"""
    # 简单的关键词匹配逻辑
    user_input_lower = user_input.lower()
    
    # 梁sx的关键词（舞蹈、情感、关心相关）
    sx_keywords = ["舞蹈", "跳舞", "心情", "情感", "关心", "体贴", "温柔", "难过", "开心", "鼓励"]
    
    # 李zm的关键词（园林、植物、专业、实际问题相关）
    zm_keywords = ["园林", "植物", "设计", "专业", "工作", "学习", "问题", "解决", "建议", "方案"]
    
    sx_score = sum(1 for keyword in sx_keywords if keyword in user_input_lower)
    zm_score = sum(1 for keyword in zm_keywords if keyword in user_input_lower)
    
    # 如果分数相同，默认选择梁sx
    if zm_score > sx_score:
        return "李zm"
    else:
        return "梁sx"

def get_ai_response(character, user_input):
    """调用DeepSeek API获取AI回复"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    system_prompt = CHARACTERS[character]["system_prompt"]
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"抱歉，AI服务暂时不可用。错误信息: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天消息"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"error": "消息不能为空"}), 400
        
        # 智能选择人物
        selected_character = select_character(user_input)
        
        # 获取AI回复
        ai_response = get_ai_response(selected_character, user_input)
        
        return jsonify({
            "character": selected_character,
            "response": ai_response,
            "character_description": CHARACTERS[selected_character]["description"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/characters', methods=['GET'])
def get_characters():
    """获取所有可用人物信息"""
    return jsonify(CHARACTERS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)