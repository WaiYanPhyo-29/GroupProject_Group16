# GroupPRoject_Group16
Smart Household Carbon Footprint Tracker

## How to Run
1. Install Python 3
2. Install Flask: pip install flask
3. make sure you navigate to the app folder:
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
  
## Technologies Used
- Python Flask for Backend
- HTML/CSS for Frontend
- SQLite for Database
- DESNZ/DEFRA 2025 Emission Factors
  
## Database Tables
- User stores login credentials
- Household store household details
- Activity store recorded activities
- Category store emission categories
- Recommendation store emission tips
