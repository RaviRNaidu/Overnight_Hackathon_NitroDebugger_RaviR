import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from xgboost import XGBClassifier
import joblib

CURRENT_DIR = Path(__file__).parent
MODELS_DIR = CURRENT_DIR / 'models'

def create_models_dir():
    MODELS_DIR.mkdir(exist_ok=True)

def load_data():
    df = pd.read_csv(CURRENT_DIR / 'processed_features.csv')
    print(f"Loaded processed_features.csv: {len(df)} rows")
    return df

def select_features(df):
    exclude_cols = {
        'txn_id', 'txn_date', 'txn_time', 'farmer_id', 'dealer_id', 'invoice_no',
        'notes', 'fraud_reason', 'name_hash', 'phone_hash', 'bank_hash',
        'owner_phone_hash', 'owner_bank_hash', 'village_id', 'village_name',
        'scheme_name', 'applicable_crops', 'effective_from', 'effective_to',
        'notes_dealer', 'notes_rule', 'is_suspected_fraud', 'scheme_id',
        'scheme_id_rule', 'scheme_rule_id', 'district', 'district_dealer',
        'district_rule', 'season', 'product_type', 'mode_of_delivery',
        'payment_mode', 'license_type', 'registered_date', 'registration_date',
        'dealer_name', 'village_id_dealer', 'village_name_dealer', 'crop_type',
        'is_ghost_farmer', 'is_active'
    }
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    numeric_features = []
    for col in feature_cols:
        if df[col].dtype in [np.float64, np.float32, np.int64, np.int32, np.int16, np.int8]:
            numeric_features.append(col)
        elif df[col].dtype == bool or df[col].dtype == 'bool':
            numeric_features.append(col)
    
    return numeric_features

def split_data(df, feature_cols):
    if 'txn_date' in df.columns:
        df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
        max_date = df['txn_date'].max()
        cutoff_date = max_date - timedelta(days=90)
        
        train_idx = df['txn_date'] < cutoff_date
        val_idx = df['txn_date'] >= cutoff_date
        
        X_train = df[train_idx][feature_cols].copy()
        X_val = df[val_idx][feature_cols].copy()
        y_train = df[train_idx].copy() if 'is_suspected_fraud' in df.columns else None
        y_val = df[val_idx].copy() if 'is_suspected_fraud' in df.columns else None
    else:
        n_train = int(len(df) * 0.7)
        train_idx = np.arange(n_train)
        val_idx = np.arange(n_train, len(df))
        
        X_train = df.iloc[train_idx][feature_cols].copy()
        X_val = df.iloc[val_idx][feature_cols].copy()
        y_train = df.iloc[train_idx].copy() if 'is_suspected_fraud' in df.columns else None
        y_val = df.iloc[val_idx].copy() if 'is_suspected_fraud' in df.columns else None
    
    print(f"Train/Val split: {len(X_train)} / {len(X_val)}")
    return X_train, X_val, y_train, y_val

def preprocess(X_train, X_val):
    X_train = X_train.fillna(X_train.median())
    X_val = X_val.fillna(X_train.median())
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    joblib.dump(scaler, MODELS_DIR / 'feature_scaler.pkl')
    
    return X_train_scaled, X_val_scaled, scaler

def compute_precision_at_k(y_true, scores, k):
    top_k_idx = np.argsort(scores)[-k:]
    return (y_true.iloc[top_k_idx].astype(int).sum() / k) if k > 0 else 0

def train_isolation_forest(X_train, X_val, y_val):
    print("Training Isolation Forest...")
    model = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)
    model.fit(X_train)
    
    train_scores = model.decision_function(X_train)
    val_scores = model.decision_function(X_val)
    
    print(f"IsolationForest trained. Saved to models/isolation_forest.pkl")
    joblib.dump(model, MODELS_DIR / 'isolation_forest.pkl')
    
    metrics = {
        'model': 'isolation_forest',
        'train_mean_score': float(np.mean(train_scores)),
        'train_std_score': float(np.std(train_scores)),
        'val_mean_score': float(np.mean(val_scores)),
        'val_std_score': float(np.std(val_scores))
    }
    
    print(f"Train anomaly score: mean={metrics['train_mean_score']:.4f}, std={metrics['train_std_score']:.4f}")
    print(f"Val anomaly score: mean={metrics['val_mean_score']:.4f}, std={metrics['val_std_score']:.4f}")
    
    if y_val is not None and 'is_suspected_fraud' in y_val.columns:
        y_true = y_val['is_suspected_fraud'].fillna(False).astype(bool)
        if y_true.sum() > 0:
            neg_scores = -val_scores
            prec_100 = compute_precision_at_k(y_true, neg_scores, 100)
            prec_500 = compute_precision_at_k(y_true, neg_scores, 500)
            print(f"IsolationForest Precision@100: {prec_100:.4f}, Precision@500: {prec_500:.4f}")
            metrics['precision_100'] = prec_100
            metrics['precision_500'] = prec_500
    
    return metrics

def train_xgboost(X_train, X_val, y_train, y_val):
    if y_train is None or 'is_suspected_fraud' not in y_train.columns:
        return None
    
    y_train_labels = y_train['is_suspected_fraud'].fillna(False).astype(int)
    y_val_labels = y_val['is_suspected_fraud'].fillna(False).astype(int)
    
    if y_train_labels.sum() == 0:
        return None
    
    print("Training XGBoost...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )
    
    model.fit(
        X_train, y_train_labels,
        eval_set=[(X_val, y_val_labels)]
    )
    
    print(f"XGBoost trained. Saved to models/xgboost_model.pkl")
    joblib.dump(model, MODELS_DIR / 'xgboost_model.pkl')
    
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    y_pred = model.predict(X_val)
    
    auc = roc_auc_score(y_val_labels, y_pred_proba)
    precision = precision_score(y_val_labels, y_pred, zero_division=0)
    recall = recall_score(y_val_labels, y_pred, zero_division=0)
    
    prec_100 = compute_precision_at_k(pd.Series(y_val_labels.values), -y_pred_proba, 100)
    prec_500 = compute_precision_at_k(pd.Series(y_val_labels.values), -y_pred_proba, 500)
    
    print(f"XGBoost ROC AUC: {auc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
    print(f"XGBoost Precision@100: {prec_100:.4f}, Precision@500: {prec_500:.4f}")
    
    metrics = {
        'model': 'xgboost',
        'auc': auc,
        'precision': precision,
        'recall': recall,
        'precision_100': prec_100,
        'precision_500': prec_500
    }
    
    return metrics

def save_metrics(if_metrics, xgb_metrics):
    summary = {
        'isolation_forest': if_metrics,
        'xgboost': xgb_metrics
    }
    
    with open(MODELS_DIR / 'metrics_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

def main():
    create_models_dir()
    
    df = load_data()
    feature_cols = select_features(df)
    
    X_train, X_val, y_train, y_val = split_data(df, feature_cols)
    X_train_scaled, X_val_scaled, scaler = preprocess(X_train, X_val)
    
    if_metrics = train_isolation_forest(X_train_scaled, X_val_scaled, y_val)
    xgb_metrics = train_xgboost(X_train_scaled, X_val_scaled, y_train, y_val)
    
    save_metrics(if_metrics, xgb_metrics)

if __name__ == '__main__':
    main()
