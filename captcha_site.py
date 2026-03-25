from flask import Flask, request, jsonify, render_template_string
import uuid

app = Flask(__name__)

# In-memory store; for production, use Redis or a database
captchas = {}

@app.route('/store', methods=['POST'])
def store():
    """Bot calls this to upload captcha HTML. Returns a unique ID."""
    data = request.get_json()
    captcha_id = str(uuid.uuid4())
    captchas[captcha_id] = {
        'html': data['html'],
        'email': data.get('email')
    }
    return jsonify({'id': captcha_id})

@app.route('/captcha/<captcha_id>', methods=['GET'])
def show_captcha(captcha_id):
    """User opens this URL to solve the captcha."""
    data = captchas.get(captcha_id)
    if not data:
        return "Invalid or expired captcha", 404
    # Replace the placeholder with the actual captcha ID
    html = data['html'].replace('__CAPTCHA_ID__', captcha_id)
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit():
    """Page calls this after captcha is solved to send token."""
    data = request.get_json()
    captcha_id = data.get('id')
    token = data.get('token')
    if captcha_id and token and captcha_id in captchas:
        captchas[captcha_id]['token'] = token
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

@app.route('/poll/<captcha_id>', methods=['GET'])
def poll(captcha_id):
    """Bot polls this endpoint to retrieve the token."""
    data = captchas.get(captcha_id)
    if not data:
        return jsonify({'token': None})
    if 'token' in data:
        token = data.pop('token')
        del captchas[captcha_id]  # clean up
        return jsonify({'token': token})
    return jsonify({'token': None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
