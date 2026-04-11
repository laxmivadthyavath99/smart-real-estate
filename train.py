import pandas as pd
import numpy as np
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# Prevent KMeans from hanging on Windows OpenMP threads
os.environ["OMP_NUM_THREADS"] = "1"

# Set reference date for relative datetimes
REF_DATE = datetime(2025, 2, 19)

def parse_date(date_str):
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    
    # Check for explicit date formats like '2025-02-19' or '2025-02-19T04:38:38.179Z'
    try:
        # Just grab the YYYY-MM-DD part if possible
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
    except ValueError:
        pass
    
    # Handle relative dates
    date_str_lower = date_str.lower()
    if 'yesterday' in date_str_lower:
        return REF_DATE - relativedelta(days=1)
    
    # Extract numbers
    match = re.search(r'(\d+)', date_str)
    if not match:
        return REF_DATE
    val = int(match.group(1))
    
    if 'mo' in date_str_lower or 'month' in date_str_lower:
        return REF_DATE - relativedelta(months=val)
    elif 'w ' in date_str_lower or 'week' in date_str_lower:
        return REF_DATE - relativedelta(weeks=val)
    elif 'd ' in date_str_lower or 'day' in date_str_lower:
        return REF_DATE - relativedelta(days=val)
        
    return REF_DATE

def parse_size(size_str):
    if pd.isna(size_str):
        return None
    size_str = str(size_str)
    # Extract all numbers from the string
    numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', size_str)]
    if not numbers:
        return None
    # If range, take average
    return sum(numbers) / len(numbers)

def clean_data(df):
    df_clean = df.copy()
    
    # Parse dates and calculate numerical timestamp (days since base)
    base_date = datetime(2020, 1, 1) # Arbitrary fixed past date
    df_clean['parsed_date'] = df_clean['date'].apply(parse_date)
    df_clean = df_clean.dropna(subset=['parsed_date'])
    df_clean['timestamp_days'] = (df_clean['parsed_date'] - base_date).dt.days
    
    # Parse sizes
    df_clean['parsed_size'] = df_clean['size'].apply(parse_size)
    
    # Convert beds/bhk to numeric
    df_clean['beds'] = pd.to_numeric(df_clean['beds'], errors='coerce')
    
    # Clean prices
    df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
    
    # Drop NAs
    df_clean = df_clean.dropna(subset=['parsed_size', 'beds', 'price'])
    
    # Drop rows with 0 price or anomalously small prices (e.g. 5.15 Cr raw instead of 51500000)
    # We will assume realistic minimum price is ~1,000,000
    df_clean = df_clean[df_clean['price'] > 100_000]
    
    return df_clean

def train_models(dataset_path):
    print("Loading data...")
    df = pd.read_csv(dataset_path)
    df = clean_data(df)
    
    print(f"Cleaned data size: {len(df)}")
    
    features = ['timestamp_days', 'parsed_size', 'beds']
    target = 'price'
    
    X = df[features]
    y = df[target]
    
    # Use user's requested 0.3 test size
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import RobustScaler
    
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Hybrid Model...")
    # 1. Base Ridge Regression (more robust than Linear)
    lr_model = Ridge(alpha=10.0)
    lr_model.fit(X_train_scaled, y_train)
    
    train_lr_preds = lr_model.predict(X_train_scaled)
    residuals = y_train - train_lr_preds
    
    # 2. Random Forest to predict the residuals
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    rf_model.fit(X_train_scaled, residuals)
    
    # Test hybrid evaluation
    test_lr_preds = lr_model.predict(X_test_scaled)
    test_residuals_preds = rf_model.predict(X_test_scaled)
    hybrid_preds = test_lr_preds + test_residuals_preds
    
    mae = mean_absolute_error(y_test, hybrid_preds)
    r2 = r2_score(y_test, hybrid_preds)
    print(f"Hybrid Model Evaluation -> MAE: {mae:,.2f}, R2: {r2:.3f}")
    
    # Group logic: KNN for categorize
    print("Training KNN for Categorization...")
    # We use KMeans to create 3 pure clusters based on [size, beds, price]
    # Cluster 0: Domestic, 1: Business, 2: Sale/Distressed
    X_clust = df[['parsed_size', 'beds', 'price']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(X_clust)
    
    # Determine which cluster is which by its centers
    centers = kmeans.cluster_centers_
    # Center dimensions: [size, beds, price]
    # Finding "Business" - likely has the highest size or price
    business_idx = np.argmax(centers[:, 0]) # Largest average size
    
    # Of the remaining two, higher price to size ratio = Domestic, lower = Deal/Sale
    remaining = [i for i in range(3) if i != business_idx]
    price_to_size_ratio = [centers[i, 2] / centers[i, 0] if centers[i, 0] > 0 else 0 for i in remaining]
    domestic_idx = remaining[np.argmax(price_to_size_ratio)]
    sale_idx = remaining[np.argmin(price_to_size_ratio)]
    
    cluster_mapping = {
        business_idx: "Business / Investment",
        domestic_idx: "Domestic Use",
        sale_idx: "Quick Sale / Deal"
    }
    
    # Train KNeighborsClassifier so new points are directly assigned
    knn = KNeighborsClassifier(n_neighbors=5)
    # Standardize classes to names
    named_y = [cluster_mapping[lbl] for lbl in cluster_labels]
    knn.fit(X_clust, named_y)
    
    print("Saving models...")
    models = {
        'lr': lr_model,
        'rf': rf_model,
        'scaler': scaler,
        'knn': knn,
        'base_date': datetime(2020, 1, 1)
    }
    joblib.dump(models, 'hybrid_knn_models.pkl')
    print("Models saved as hybrid_knn_models.pkl successfully!")

if __name__ == "__main__":
    train_models('real_estate_dataset.csv')
