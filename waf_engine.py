import math
from flask import Flask, request, jsonify
import urllib.parse
import base64

app = Flask(__name__)

def calculate_entropy(text):
    if not text:
        return 0
    entropy = 0
    for x in range(256):
        p_x = text.count(chr(x)) / len(text)
        if p_x > 0:
            entropy += -p_x * math.log2(p_x)
    return entropy

def normalize_payload(raw_data):
    decoded = raw_data
    try:
        prev = None
        while decoded != prev:
            prev = decoded
            decoded = urllib.parse.unquote(decoded)
        
        if len(decoded) % 4 == 0 and any(c.isupper() for c in decoded):
            try:
                b64_decoded = base64.b64decode(decoded).decode('utf-8', errors='ignore')
                if b64_decoded.isprintable() and len(b64_decoded) > 0:
                    decoded = b64_decoded
            except Exception:
                pass
    except Exception:
        pass
    return decoded

@app.route('/api/v1/resource', methods=['GET', 'POST'])
def mock_backend():
    user_input = request.args.get('input', '') or request.form.get('input', '')
    
    normalized = normalize_payload(user_input)
    entropy_val = max(calculate_entropy(user_input), calculate_entropy(normalized))
    
    if entropy_val > 2.5:
        return jsonify({
            "status": "blocked",
            "reason": "High entropy payload detected",
            "entropy_score": round(entropy_val, 2)
        }), 403
        
    return jsonify({
        "status": "success",
        "message": "Request processed by backend securely.",
        "received_input": user_input,
        "entropy_score": round(entropy_val, 2)
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
