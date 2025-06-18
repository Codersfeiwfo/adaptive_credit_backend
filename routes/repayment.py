from flask import Blueprint, request, jsonify
import pandas as pd
import os
from datetime import datetime

repayment_bp = Blueprint('repayment', __name__)

@repayment_bp.route('/generate-schedule', methods=['POST'])
def generate_schedule():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read and parse the CSV file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['month', 'income']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'CSV must contain "month" and "income" columns'}), 400
        
        # TODO: Implement schedule generation logic
        # This is a placeholder response
        schedule = {
            'status': 'success',
            'message': 'Schedule generation endpoint is ready',
            'data': df.to_dict(orient='records')
        }
        
        return jsonify(schedule)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 