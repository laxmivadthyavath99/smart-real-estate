# 🏠 Smart Real Estate — AI Property Investment Analysis System

> A machine learning–powered web application for property price prediction, future value estimation, and investment decision support — built on real Bangalore housing market data.

🔗 **Live Demo:** [smart-real-estate-production-52d5.up.railway.app](https://smart-real-estate-production-52d5.up.railway.app)

---

## 📌 Overview

Smart Real Estate is an end-to-end AI decision support system that helps buyers, sellers, and investors make data-driven real estate decisions. It combines a hybrid ML model (Ridge Regression + Random Forest) for price prediction with KNN-based property categorization, all served through a Flask web backend.

The system was trained on 288 real listings scraped from 99acres.com covering the Bangalore property market.

---

## 🎯 Problem Statement

Real estate investment decisions are often plagued by incomplete market data, inconsistent pricing, and a lack of analytical tools. Buyers and investors are forced to rely on manual research and intuition.

This system addresses that gap by using machine learning to analyze property attributes and historical pricing trends — delivering accurate valuations and investment-grade insights instantly.

---

## ✨ Features

### 🔮 Property Price Prediction
Predicts current market price using:
- Property area (sq ft)
- Number of BHK (bedrooms)
- Temporal market trends (date-based features)

### 📈 Future Value Estimation
Projects future property value using a hybrid ML extrapolation combined with CAGR fallback logic for robust long-term estimates.

### 💼 Investment Analytics
Returns a full investment report including:
- **ROI %** — Return on investment over the chosen period
- **Expected Profit** — Absolute gain in INR
- **Risk Category** — Low / Medium / High
- **Recommendation** — Invest / Moderate Risk / Avoid / Strong Buy

### 🏷️ Property Classification
Automatically categorizes each property into:
- `Business / Investment` — High area, commercial potential
- `Domestic Use` — Standard residential
- `Quick Sale / Deal` — Distressed asset, strong buy signal

### 🧠 Hybrid ML Architecture
- **Ridge Regression** as the base model (robust to outliers)
- **Random Forest** trained on residuals for non-linear correction
- **KMeans + KNN** pipeline for unsupervised property categorization

---

## 🗂️ Project Structure

```
smart-real-estate/
├── app.py                   # Flask backend + REST API
├── train.py                 # ML training pipeline
├── hybrid_knn_models.pkl    # Pre-trained model bundle
├── real_estate_dataset.csv  # 288 Bangalore listings (99acres)
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/gunicorn deployment config
├── templates/
│   └── index.html           # Frontend UI
└── static/
    ├── css/                 # Stylesheets
    └── js/                  # Client-side scripts
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Gunicorn |
| ML Models | scikit-learn (Ridge, RandomForest, KMeans, KNN) |
| Data Processing | pandas, numpy, python-dateutil |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Railway |
| Data Source | 99acres.com (Bangalore listings) |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Git

### Steps

```bash
# Clone the repo
git clone https://github.com/Vaishnavi-A-Das/smart-real-estate.git
cd smart-real-estate

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open → **http://localhost:5000**

### (Optional) Retrain the Model

```bash
python train.py
```

> The repo ships with a pre-trained `hybrid_knn_models.pkl` — retraining is only needed if you update the dataset.

---

## 📡 API Reference

### `POST /api/predict`

**Request Body:**
```json
{
  "area": 1200,
  "bhk": 3,
  "expectedGrowth": 7.5,
  "investmentPeriod": 5
}
```

**Response:**
```json
{
  "predicted_price": 8500000.0,
  "future_value": 12045678.5,
  "roi_percentage": 41.71,
  "profit": 3545678.5,
  "recommendation": "Invest",
  "market_segment": "Mid-Range",
  "risk_category": "Low",
  "property_category": "Domestic Use"
}
```

---

## 🧪 Model Performance

| Metric | Value |
|---|---|
| Algorithm | Ridge + RandomForest Hybrid |
| Train/Test Split | 70 / 30 |
| Evaluation | MAE, R² Score |
| Categorization | KMeans (3 clusters) → KNN Classifier |

---

## 🗺️ System Workflow

```
User Input (Area, BHK, Growth Rate, Investment Period)
        ↓
Flask REST API (/api/predict)
        ↓
Data Preprocessing (scaling, date encoding)
        ↓
Hybrid ML Model (Ridge + Random Forest)
        ↓
KNN Property Categorization
        ↓
Investment Analytics (ROI, Profit, Risk, Recommendation)
        ↓
Result Dashboard
```

---

## 👩‍💻 Authors

Both authors contributed equally to this project.

- [Vaishnavi A Das](https://github.com/Vaishnavi-A-Das)
- [Laxmi Vadthyavath](https://github.com/laxmivadthyavath99)

---

## 📄 License

This project is for academic and research purposes.