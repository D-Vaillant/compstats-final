from flask import Blueprint, render_template, jsonify, request
from learning.graph import generate_points, Point
from learning.learner import fit_curve, calculate_error
from learning.db import json_query, get_species_locations
from learning.kde import fit_and_calculate, optimize_bandwidth
import duckdb
import polars as pl

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
        bandwidth_x = float(data.get('bandwidth_x'))
        bandwidth_y = float(data.get('bandwidth_y'))

        kernel_type = data.get('kernel', 'normal')
        
        # Generate different sets of points
        sampled_points = [Point(**p) for p in data['sampled_points']]
        ground_truth = [Point(**p) for p in data['ground_truth']]
        
        
        fitted_points = fit_curve(sampled_points,
                                  bandwidth_x=bandwidth_x,
                                  bandwidth_y=bandwidth_y,
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
        return jsonify({'points': points,
                        'mse': calculate_error(ground_truth, fitted_points)})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/nyc')
def nyc():
    return render_template('nyc.html')

available_birds = ['Baeolophus bicolor', 'Cyanocitta cristata', 'Sitta carolinensis']

@bp.route('/nyc/locs', methods=['GET'])
def nyc_locs():
    species = request.args.get('species', available_birds[0])
    # df = pl.read_csv("secondbirds.csv")
    # SQL INJECTION ALERT
    res = json_query(f"SELECT decimalLatitude, decimalLongitude, ifnull(individualCount, 1) AS individualCount FROM birds.parquet WHERE species = '{species}' LIMIT 1500")
    return res

@bp.route('/nyc/densities', methods=['GET'])
def nyc_kde():
    species = request.args.get('species', available_birds[0])
    sw = get_species_locations(species).fetchnumpy()
    K = fit_and_calculate(sw)
    # Calculate the KDE.
    return jsonify(K.tolist())

@bp.route('/nyc/densities/refine', methods=['GET'])
def nyc_bandwidth():
    species = request.args.get('species', available_birds[0])
    sw = get_species_locations(species).fetchnumpy()
    bandwidth_matrix = optimize_bandwidth(sw)
    K = fit_and_calculate(sw, bandwidth_matrix)
    # Calculate the KDE.
    return jsonify(K.tolist())