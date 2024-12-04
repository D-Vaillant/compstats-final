from flask import Blueprint, render_template, jsonify, request
from learning.graph import generate_points, Point
from learning.learner import fit_curve, calculate_error

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
        noise = float(request.args.get('noise', 0.0))
        # bandwidth = float(request.args.get('bw', 0.1))
        # kernel = str(request.get.args('kernel', 'normal'))
        # n_points = int(request.args.get('n_points', 1000))
        n_sampled = int(request.args.get('n_sampled', 25))
        
        ground_truth, sampled_points = generate_points(A, a, B, b, phase, n_sampled, noise)
        
        return jsonify({
            'groundTruth': [{
                't': p.t,
                'x': p.x,
                'y': p.y,
                'is_point': p.is_point,
                'color': p.color
            } for p in ground_truth],
            'sampledPoints': [{
                't': p.t,
                'x': p.x,
                'y': p.y,
                'is_point': p.is_point,
                'color': p.color
            } for p in sampled_points],
            'predicted': []
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@bp.route('/fit_points', methods=['POST'])
def fit_points():
    try:
        data = request.get_json()
        bandwidth = data.get('bandwidth')
        kernel_type = data.get('kernel', 'normal')
        
        # Generate different sets of points
        sampled_points = [Point(**p) for p in data['sampled_points']]
        ground_truth = [Point(**p) for p in data['ground_truth']]
        
        
        fitted_points = fit_curve(sampled_points,
                                  bandwidth=float(bandwidth),
                                  kernel=kernel_type)
        
        points = {
            'groundTruth': [{
                't': p.t,
                'x': p.x,
                'y': p.y,
                'is_point': p.is_point,
                'color': p.color
            } for p in ground_truth],
            'sampledPoints': [{
                't': p.t,
                'x': p.x,
                'y': p.y,
                'is_point': p.is_point,
                'color': p.color
            } for p in sampled_points],
            'predicted': [{
                't': p.t,
                'x': p.x,
                'y': p.y,
                'is_point': p.is_point,
                'color': p.color
            } for p in fitted_points]
        }
        return jsonify({'points': points, 'error': calculate_error(ground_truth, )})

    except Exception as e:
        return jsonify({'error': str(e)}), 400