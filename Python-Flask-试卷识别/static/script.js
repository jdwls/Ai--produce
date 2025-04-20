// 全局变量
let canvas, ctx;
let isDrawing = false;
let startX, startY;
let rectangles = []; // 存储所有绘制的矩形
let currentTemplate = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('templateCanvas');
    if (canvas) {
        ctx = canvas.getContext('2d');
        setupCanvasEvents();
    }
});

// 设置画布事件
function setupCanvasEvents() {
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // 绑定按钮事件
    const rectBtn = document.getElementById('rectBtn');
    if (rectBtn) {
        rectBtn.addEventListener('click', () => {
            alert('请在画布上拖动鼠标绘制答案区域');
        });
    }
    
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveTemplate);
    }
}

// 加载图片到画布
function loadImage() {
    const fileInput = document.getElementById('templateFile');
    if (fileInput.files.length === 0) return;
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            currentTemplate = img;
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// 开始绘制
function startDrawing(e) {
    isDrawing = true;
    startX = e.offsetX;
    startY = e.offsetY;
}

// 绘制过程
function draw(e) {
    if (!isDrawing) return;
    
    // 清除临时矩形
    redrawCanvas();
    
    // 绘制新矩形
    const width = e.offsetX - startX;
    const height = e.offsetY - startY;
    
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 2;
    ctx.strokeRect(startX, startY, width, height);
}

// 停止绘制
function stopDrawing(e) {
    if (!isDrawing) return;
    isDrawing = false;
    
    const width = e.offsetX - startX;
    const height = e.offsetY - startY;
    
    if (Math.abs(width) > 5 && Math.abs(height) > 5) {
        rectangles.push({
            x: startX,
            y: startY,
            width: width,
            height: height,
            answer: prompt('请输入此区域的答案:'),
            score: parseFloat(prompt('请输入此题的分数:')) || 0
        });
    }
    
    redrawCanvas();
}

// 重绘画布
function redrawCanvas() {
    if (!currentTemplate) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(currentTemplate, 0, 0);
    
    // 绘制所有保存的矩形
    rectangles.forEach(rect => {
        ctx.strokeStyle = '#FF0000';
        ctx.lineWidth = 2;
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
        
        // 显示答案和分数
        ctx.fillStyle = '#FF0000';
        ctx.font = '14px Arial';
        ctx.fillText(`${rect.answer} (${rect.score}分)`, rect.x, rect.y - 5);
    });
}

// 保存模板
function saveTemplate() {
    if (rectangles.length === 0) {
        alert('请先绘制答案区域');
        return;
    }
    
    const templateData = {
        imageWidth: canvas.width,
        imageHeight: canvas.height,
        rectangles: rectangles
    };
    
    // 获取上传的图片文件
    const fileInput = document.getElementById('templateFile');
    if (fileInput.files.length === 0) {
        alert('请先上传答题卡模板图片');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('data', JSON.stringify(templateData));
    
    fetch('/save_template', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`模板保存成功: ${data.template}`);
            location.reload(); // 刷新页面显示新模板
        } else {
            alert(`保存失败: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存过程中发生错误');
    });
}

// 上传答题卡识别
function uploadAnswerSheet() {
    const fileInput = document.getElementById('answerSheetFile');
    if (fileInput.files.length === 0) {
        alert('请选择答题卡文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/recognize', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('scoreResult').innerHTML = `
                <p>识别完成!</p>
                <p>得分: ${data.score}/100</p>
                <p>答案: ${data.answers.join(', ')}</p>
            `;
        } else {
            alert(`识别失败: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('识别过程中发生错误');
    });
}
