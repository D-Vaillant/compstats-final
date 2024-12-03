from flask import Blueprint, render_template, jsonify, request
from learning.graph import generate_points, Point
from learning.learner import fit_curve

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/get_points', methods=['GET'])
def get_points():
    try:
        # Get parameters from query string
        A = float(request.args.get('A', 1.0))
        a = float(request.args.get('a', 1.0))
        B = float(request.args.get('B', 1.0))
        b = float(request.args.get('b', 1.0))
        phase = float(request.args.get('phase', 0.0))
        # n_points = int(request.args.get('n_points', 1000))
        n_sampled = int(request.args.get('n_sampled', 10))
        
        points = generate_points(A, a, B, b, phase, n_sampled)
        
        return jsonify([{
            't': p.t,
            'x': p.x,
            'y': p.y,
            'is_point': p.is_point,
            'color': p.color
        } for p in points])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@bp.route('/fit_points', methods=['POST'])
def fit_points():
    try:
        data = request.get_json()
        sampled_points = [Point(**p) for p in data]
        fitted_points = fit_curve(sampled_points)
        
        return jsonify([{
            't': p.t,
            'x': p.x,
            'y': p.y,
            'is_point': p.is_point,
            'color': p.color
        } for p in fitted_points])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400