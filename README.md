# SmartRepayment

SmartRepayment is a web application that helps users create flexible loan repayment schedules based on their income patterns.

## Project Structure

```
├── backend/           # Python Flask backend
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── tests/
└── frontend/         # React frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── api/
    └── public/
```

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `python app.py`

### Frontend Setup
1. Navigate to the frontend directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## Features
- Upload and parse income data from CSV files
- Generate flexible repayment schedules based on income patterns
- Visualize repayment plans with interactive charts
- Export repayment plans as PDF documents 
