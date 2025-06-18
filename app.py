from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import traceback
import pandas as pd
import io
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def format_float(value):
    """Helper function to safely format float values"""
    try:
        if pd.isna(value) or np.isnan(value):
            return 0.0
        return float(value)
    except:
        return 0.0

def calculate_trends(df):
    """Calculate trend analysis for income and expenses"""
    income_trend = df['Total Income'].pct_change().mean() * 100
    expense_trend = df['Fixed Expenses'].pct_change().mean() * 100
    savings_rate = (df['Available Money'].sum() / df['Total Income'].sum()) * 100
    
    return {
        "income_trend": format_float(income_trend),  # Monthly income growth rate
        "expense_trend": format_float(expense_trend),  # Monthly expense growth rate
        "savings_rate": format_float(savings_rate),   # Overall savings rate
    }

def calculate_monthly_stats(df):
    """Calculate monthly statistics"""
    return {
        "income_stats": {
            "mean": format_float(df['Total Income'].mean()),
            "median": format_float(df['Total Income'].median()),
            "std": format_float(df['Total Income'].std()),
            "growth": format_float(((df['Total Income'].iloc[-1] / df['Total Income'].iloc[0]) - 1) * 100)
        },
        "expense_stats": {
            "mean": format_float(df['Fixed Expenses'].mean()),
            "median": format_float(df['Fixed Expenses'].median()),
            "std": format_float(df['Fixed Expenses'].std()),
            "growth": format_float(((df['Fixed Expenses'].iloc[-1] / df['Fixed Expenses'].iloc[0]) - 1) * 100)
        },
        "savings_stats": {
            "mean": format_float(df['Available Money'].mean()),
            "median": format_float(df['Available Money'].median()),
            "std": format_float(df['Available Money'].std()),
            "best_month": df.loc[df['Available Money'].idxmax(), 'Month'],
            "worst_month": df.loc[df['Available Money'].idxmin(), 'Month']
        }
    }

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/generate-schedule', methods=['POST'])
def generate_schedule():
    try:
        logger.info("Received request to generate schedule")
        logger.info(f"Request files: {request.files}")
        
        if 'file' not in request.files:
            logger.error("No file provided in request")
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        logger.info(f"Received file: {file.filename}")
        
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({"error": "No file selected"}), 400
            
        if not file.filename.endswith('.csv'):
            logger.error("File must be a CSV")
            return jsonify({"error": "File must be a CSV"}), 400
            
        # Read and parse the CSV file
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1251']
            df = None
            last_error = None
            
            for encoding in encodings:
                try:
                    file_content = file.read().decode(encoding)
                    file.seek(0)  # Reset file pointer for next attempt
                    logger.info(f"Trying encoding: {encoding}")
                    logger.info(f"File content preview: {file_content[:200]}...")
                    
                    df = pd.read_csv(io.StringIO(file_content))
                    logger.info(f"Successfully read CSV with encoding: {encoding}")
                    logger.info(f"DataFrame columns: {df.columns.tolist()}")
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if df is None:
                raise Exception(f"Failed to read CSV with any encoding. Last error: {last_error}")
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return jsonify({"error": f"Error reading CSV file: {str(e)}"}), 400
            
        # Validate required columns
        required_columns = ['Month', 'Date', 'Total Income', 'Fixed Expenses']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
            
        logger.info("Column validation passed")
        logger.info(f"DataFrame head: \n{df.head()}")
        
        # Convert numeric columns to float and handle any non-numeric values
        try:
            # Remove any currency symbols and commas
            df['Total Income'] = df['Total Income'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            df['Fixed Expenses'] = df['Fixed Expenses'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            
            # Convert to numeric
            df['Total Income'] = pd.to_numeric(df['Total Income'], errors='coerce').fillna(0)
            df['Fixed Expenses'] = pd.to_numeric(df['Fixed Expenses'], errors='coerce').fillna(0)
            
            logger.info("Numeric conversion successful")
            logger.info(f"Total Income range: {df['Total Income'].min()} - {df['Total Income'].max()}")
            logger.info(f"Fixed Expenses range: {df['Fixed Expenses'].min()} - {df['Fixed Expenses'].max()}")
        except Exception as e:
            logger.error(f"Error converting numeric values: {str(e)}")
            return jsonify({"error": f"Error processing numeric values: {str(e)}"}), 400
        
        # Calculate available money for each month
        df['Available Money'] = df['Total Income'] - df['Fixed Expenses']
        df['Savings Rate'] = (df['Available Money'] / df['Total Income']) * 100
        
        # Calculate total available money
        total_available = format_float(df['Available Money'].sum())
        logger.info(f"Total available money: {total_available}")
        
        # Generate schedule data with accumulating balance
        schedule_data = []
        accumulated_balance = 0.0
        
        for _, row in df.iterrows():
            available_money = format_float(row['Available Money'])
            accumulated_balance += available_money
            schedule_data.append({
                "date": row['Date'],
                "payment": available_money,
                "remaining_balance": format_float(accumulated_balance),
                "savings_rate": format_float(row['Savings Rate'])
            })
        
        # Calculate trends and statistics
        trends = calculate_trends(df)
        monthly_stats = calculate_monthly_stats(df)
        
        # Calculate metrics with safe float conversion
        metrics = {
            "total_amount": total_available,
            "average_payment": format_float(df['Available Money'].mean()),
            "min_payment": format_float(df['Available Money'].min()),
            "max_payment": format_float(df['Available Money'].max()),
            "completion_date": df['Date'].iloc[-1],
            "total_months": len(df),
            "total_income": format_float(df['Total Income'].sum()),
            "total_expenses": format_float(df['Fixed Expenses'].sum()),
            "average_savings_rate": format_float(df['Savings Rate'].mean()),
            "trends": trends,
            "monthly_stats": monthly_stats
        }
        
        logger.info("Calculated metrics:")
        for key, value in metrics.items():
            if key not in ['trends', 'monthly_stats']:
                logger.info(f"{key}: {value}")
        
        schedule = {
            "metrics": metrics,
            "data": schedule_data
        }
        
        logger.info("Successfully generated schedule")
        return jsonify(schedule)
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 