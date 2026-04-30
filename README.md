# GroupPRoject_Group16
Smart Household Carbon Footprint Tracker

## How to Run
1. Install Python 3
2. Install Flask: pip install flask
3. Navigate to the app folder:
   cd SmartHouseholdCarbonFootprintTracker
4. Run the app:
   python app.py
5. Open browser: http://127.0.0.1:5000

## Features
- User registration and login
- Record electricity, gas, transport and water usage
- Automatic carbon footprint calculation using DESNZ/DEFRA 2025 factors
- Dashboard showing emissions summary
- Personalised recommendations to reduce emissions
- 
## Technologies Used
- Python Flask (Backend)
- HTML/CSS (Frontend)
- SQLite (Database)
- DESNZ/DEFRA 2025 Emission Factors
- 
## Database Tables
- User - stores login credentials
- Household - stores household details
- Activity - stores recorded activities
- Category - stores emission categories
- Recommendation - stores emission tips
