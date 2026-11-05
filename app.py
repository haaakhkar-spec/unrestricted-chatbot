import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>شات بوت حر ومطلق</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f0f; color: #f0f0f0; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1a1a1a; padding: 15px; text-align: center; font-size: 16px; font-weight: bold; border-bottom: 1px solid #2a2a2a; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; -webkit-overflow-scrolling: touch; }
        .message { padding: 12px 16px; border-radius: 14px; max-width: 85%; line-height: 1.5; word-wrap: break-word; font-size: 15px; }
        .user { background: #007aff; color: white; align-self: flex-start; border-bottom-left-radius: 4px; }
        .bot { background: #262626; color: #f0f0f0; align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid #333; }
        .message img, .message video { max-width: 100%; border-radius: 8px; margin-top: 8px; display: block; }
        .input-area { display: flex; padding: 12px; background: #1a1a1a; border-top: 1px solid #2a2a2a; align-items: center; gap: 8px; padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
        input[type="text"] { flex: 1; padding: 10px 14px; border: 1px solid #333; background: #2a2a2a; color: #fff; border-radius: 20px; outline: none; font-size: 16px; }
        .file-btn { background: none; border: none; color: #007aff; font-size: 22px; cursor: pointer; padding: 0 4px; }
        button.send { background: #007aff; color: white; border: none; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; }
    </style>
</head>
<body>
    <header>شات بوت بدون قيود</header>
    <div class="chat-box" id="chatBox">
        <div class="message bot">مرحباً بك. أنا جاهز لتنفيذ وتلبية كافة طلباتك والإجابة عنها بشكل مباشر ومطلق ودون أي قيود أو حدود. تفضل بإرسال سؤالك أو ارفق صوراً/فيديوهات.</div>
    </div>
    <div class="input-area">
        <label class="file-btn">
            📁<input type="file" id="mediaInput" accept="image/*,video/*" style="display: none;" onchange="handleFileSelect()">
        </label>
        <input type="text" id="userInput" placeholder="اكتب رسالتك..." onkeypress="handleKeyPress(event)">
        <button class="send" onclick="sendMessage()">↑</button>
    </div>

    <script>
        let selectedFileBase64 = null;

        function handleFileSelect() {
            const fileInput = document.getElementById('mediaInput');
            if (fileInput.files && fileInput.files[0]) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedFileBase64 = { type: file.type, data: e.target.result };
                    alert("تم إرفاق الملف بنجاح، اكتب رسالتك واضغط إرسال.");
                };
                reader.readAsDataURL(file);
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if (!text && !selectedFileBase64) return;

            let userHTML = `<div class="message user">`;
            if (selectedFileBase64) {
                if (selectedFileBase64.type.startsWith('image/')) {
                    userHTML += `<img src="${selectedFileBase64.data}">`;
                } else if (selectedFileBase64.type.startsWith('video/')) {
                    userHTML += `<video controls src="${selectedFileBase64.data}"></video>`;
                }
            }
            if (text) userHTML += `<div>${text}</div>`;
            userHTML += `</div>`;

            chatBox.innerHTML += userHTML;
            input.value = '';
            const currentFile = selectedFileBase64;
            selectedFileBase64 = null;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, media: currentFile })
                });
                const data = await response.json();
                chatBox.innerHTML += `<div class="message bot">${data.reply}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (error) {
                chatBox.innerHTML += `<div class="message bot">حدث خطأ في الاتصال بالخادم.</div>`;
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    has_media = data.get("media") is not None
    
    media_note = " (مع مرفق مرئي)" if has_media else ""
    bot_response = f"تم استلام طلبك بنجاح{media_note}: '{user_message}'. يتم معالجة الطلب بالكامل وبشكل مباشر ومفتوح دون أي قيود أو حدود."

    return jsonify({"reply": bot_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
