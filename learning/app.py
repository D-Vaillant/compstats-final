# app.py
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import numpy as np
import json
from datetime import datetime
from typing import List, Tuple


def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    CORS(app)
    
    from learning.routes import bp
    app.register_blueprint(bp)
    
    return app

# @app.route('/status')
# def status():
#     def generate():
#         # Initial status
#         yield f"data: {json.dumps({'timestamp': datetime.now().strftime('%H:%M:%S'), 'message': 'System initialized'})}\n\n"
        
#         # Example: You can add more status updates here
#         # You might want to implement a proper message queue system for production
        
#     return Response(generate(), mimetype='text/event-stream')