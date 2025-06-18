from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import joblib
import os
import json
from utils.attack_simulator import AttackSimulator
from utils.data_processor import DataProcessor
from utils.feature_extractor import FeatureExtractor

app = Flask(__name__)

# Initialize components
data_processor = DataProcessor('dataset/nsl_kdd.csv')
attack_simulator = AttackSimulator()
feature_extractor = FeatureExtractor()

# Load attack types from the dataset
attack_types = data_processor.get_attack_types()

@app.route('/')
def index():
    """Render the main portal interface"""
    return render_template('index.html', attack_types=attack_types)

@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    """Simulate an attack based on user input"""
    target_url = request.form.get('target_url')
    attack_type = request.form.get('attack_type')
    intensity = int(request.form.get('intensity', 1))
    
    if not target_url:
        return jsonify({'error': 'Target URL is required'}), 400
    
    # Start the attack simulation
    simulation_id = attack_simulator.start_simulation(
        target_url=target_url,
        attack_type=attack_type,
        intensity=intensity
    )
    
    return jsonify({
        'simulation_id': simulation_id,
        'status': 'started',
        'message': f'Started {attack_type} simulation against {target_url}'
    })

@app.route('/simulation_status/<simulation_id>')
def simulation_status(simulation_id):
    """Get the status of a running simulation"""
    status = attack_simulator.get_simulation_status(simulation_id)
    return jsonify(status)

@app.route('/stop_simulation/<simulation_id>')
def stop_simulation(simulation_id):
    """Stop a running simulation"""
    result = attack_simulator.stop_simulation(simulation_id)
    return jsonify(result)

@app.route('/blocked')
def blocked():
    """Render the blocked page"""
    reason = request.args.get('reason', 'Suspicious activity detected')
    return render_template('blocked.html', reason=reason)

@app.route('/attack_details/<attack_type>')
def attack_details(attack_type):
    """Get details about a specific attack type"""
    details = data_processor.get_attack_details(attack_type)
    return jsonify(details)

@app.route('/dataset_stats')
def dataset_stats():
    """Get statistics about the dataset"""
    stats = data_processor.get_dataset_stats()
    return jsonify(stats)

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
