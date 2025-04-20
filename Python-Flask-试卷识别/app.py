from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import cv2
import numpy as np
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATE_FOLDER'] = 'templates_data'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMPLATE_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_image(image_path):
    """基础图像处理"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    # 二值化处理
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary

@app.route('/')
def index():
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    # 获取已保存的模板列表
    templates = []
    if os.path.exists(app.config['TEMPLATE_FOLDER']):
        templates = [f for f in os.listdir(app.config['TEMPLATE_FOLDER']) 
                   if f.endswith('.json')]
    return render_template('admin.html', templates=templates)

@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

@app.route('/save_template', methods=['POST'])
def save_template():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 处理模板数据
        template_data = request.form.get('data')
        if not template_data:
            return jsonify({'error': 'No template data'}), 400
            
        try:
            data = json.loads(template_data)
            # 保存模板数据
            template_name = f"template_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            with open(os.path.join(app.config['TEMPLATE_FOLDER'], template_name), 'w') as f:
                json.dump(data, f)
                
            return jsonify({'success': True, 'template': template_name})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 加载最新保存的模板
        templates = sorted([f for f in os.listdir(app.config['TEMPLATE_FOLDER']) 
                      if f.endswith('.json')], reverse=True)
        if not templates:
            return jsonify({'error': '没有可用的模板'}), 400
            
        with open(os.path.join(app.config['TEMPLATE_FOLDER'], templates[0]), 'r') as f:
            template = json.load(f)
        
        # 处理答题卡图像
        img = process_image(filepath)
        if img is None:
            return jsonify({'error': '图像处理失败'}), 400
            
        # 识别每个答案区域
        answers = []
        total_score = 0
        for i, rect in enumerate(template['rectangles']):
            x, y, w, h = int(rect['x']), int(rect['y']), int(rect['width']), int(rect['height'])
            roi = img[y:y+h, x:x+w]
            
            # 计算区域内黑色像素比例
            black_pixels = np.sum(roi == 255)
            total_pixels = roi.size
            ratio = black_pixels / total_pixels
            
            # 如果黑色像素超过30%则认为被选中
            if ratio > 0.3:
                answers.append(rect['answer'])
                total_score += rect['score']
            else:
                answers.append('')
        
        return jsonify({
            'success': True,
            'score': total_score,
            'answers': answers
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
