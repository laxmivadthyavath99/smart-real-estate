from flask import Flask, render_template, request, jsonify
import random
import joblib
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

# Load ML models on start
try:
    models = joblib.load('hybrid_knn_models.pkl')
    has_models = True
except Exception as e:
    print(f"Warning: ML Models not found or failed to load. Using fallback logic. ({e})")
    has_models = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Parse inputs
    area = int(data.get('area', 1000))
    bhk = int(data.get('bhk', 2))
    growth_rate = float(data.get('expectedGrowth', 5.0))
    years = int(data.get('investmentPeriod', 5))
    
    # Defaults
    recommendation = "Invest"
    risk_category = "Low"
    property_category = "Domestic Use"
    
    if has_models:
        base_date = models['base_date']
        current_date = datetime.now()
        future_date = current_date + relativedelta(years=years)
        
        current_days = (current_date - base_date).days
        future_days = (future_date - base_date).days
        
        # Current Price Prediction (Hybrid)
        X_curr = models['scaler'].transform([[current_days, area, bhk]])
        base_price_lr = models['lr'].predict(X_curr)[0]
        residual_rf = models['rf'].predict(X_curr)[0]
        predicted_price = base_price_lr + residual_rf
        
        # Fix extreme negatives if model extrapolates poorly backwards
        if predicted_price <= 0:
            predicted_price = (area * 5000) + (bhk * 500000)
            
        # Future Value Extrapolation (Hybrid)
        X_fut = models['scaler'].transform([[future_days, area, bhk]])
        future_lr = models['lr'].predict(X_fut)[0]
        future_residual = models['rf'].predict(X_fut)[0]
        future_value = future_lr + future_residual
        
        # If extrapolation curve goes negative/flatlines wrong, fallback to standard CAGR
        if future_value <= predicted_price:
            future_value = predicted_price * ((1 + (growth_rate / 100)) ** years)
            
        # Unsupervised Categorization (KNN)
        # Using [size, beds, price] as features
        import pandas as pd
        cluster_df = pd.DataFrame(data=[[float(area), float(bhk), predicted_price]], columns=['parsed_size', 'beds', 'price'])
        property_category = models['knn'].predict(cluster_df)[0]
        
    else:
        # Fallback Mock Logic
        base_price = (area * 5000) + (bhk * 500000)
        predicted_price = base_price * random.uniform(0.9, 1.2)
        future_value = predicted_price * ((1 + (growth_rate / 100)) ** years)

    # Derived metrics
    roi_percentage = ((future_value - predicted_price) / predicted_price) * 100
    profit = future_value - predicted_price
    
    # Static logic based on value
    market_segment = "Premium" if predicted_price > 10000000 else ("Mid-Range" if predicted_price > 5000000 else "Budget")
    
    if roi_percentage < 20:
        recommendation = "Moderate Risk"
        risk_category = "Medium"
    if roi_percentage < 5:
        recommendation = "Avoid"
        risk_category = "High"
        
    # Introduce Quick Sale concept natively
    if property_category == "Quick Sale / Deal":
        recommendation = "Strong Buy (Distressed Asset)"
        risk_category = "Low"

    return jsonify({
        "predicted_price": round(predicted_price, 2),
        "future_value": round(future_value, 2),
        "roi_percentage": round(roi_percentage, 2),
        "profit": round(profit, 2),
        "recommendation": recommendation,
        "market_segment": market_segment,
        "risk_category": risk_category,
        "property_category": property_category
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
