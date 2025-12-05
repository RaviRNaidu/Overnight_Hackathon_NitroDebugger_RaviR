import os
import pandas as pd
import numpy as np
from pathlib import Path
from haversine import haversine

CURRENT_DIR = Path(__file__).parent

def load_data():
    print("Loading datasets...")
    farmers = pd.read_csv(CURRENT_DIR / 'farmers.csv')
    dealers = pd.read_csv(CURRENT_DIR / 'dealers.csv')
    transactions = pd.read_csv(CURRENT_DIR / 'transactions.csv')
    scheme_rules = pd.read_csv(CURRENT_DIR / 'scheme_rules.csv')
    return farmers, dealers, transactions, scheme_rules

def perform_joins(farmers, dealers, transactions, scheme_rules):
    print("Performing joins...")
    
    df = transactions.copy()
    
    df = df.merge(farmers, on='farmer_id', how='left', suffixes=('', '_farmer'))
    df = df.merge(dealers, on='dealer_id', how='left', suffixes=('', '_dealer'))
    
    scheme_rules_dedup = scheme_rules.drop_duplicates(subset=['product_type', 'season']).copy()
    df = df.merge(scheme_rules_dedup, on=['product_type', 'season'], how='left', suffixes=('', '_rule'))
    
    return df

def create_farmer_features(df):
    print("Creating farmer-derived features...")
    
    df['quantity_per_hectare'] = df['quantity_kg'] / np.maximum(df['claimed_land_area_ha'], 0.1)
    
    df['land_vs_claim_diff'] = df['claimed_land_area_ha'] - df['land_holding_ha']
    
    farmer_txn_count = df.groupby('farmer_id').size().reset_index(name='farmer_total_transactions')
    df = df.merge(farmer_txn_count, on='farmer_id', how='left')
    
    farmer_total_qty = df.groupby('farmer_id')['quantity_kg'].sum().reset_index(name='farmer_total_quantity')
    df = df.merge(farmer_total_qty, on='farmer_id', how='left')
    
    return df

def create_dealer_features(df):
    print("Creating dealer-derived features...")
    
    dealer_unique_farmers = df.groupby('dealer_id')['farmer_id'].nunique().reset_index(name='dealer_total_farmers')
    df = df.merge(dealer_unique_farmers, on='dealer_id', how='left')
    
    dealer_txn_count = df.groupby('dealer_id').size().reset_index(name='dealer_total_transactions')
    df = df.merge(dealer_txn_count, on='dealer_id', how='left')
    
    dealer_total_qty = df.groupby('dealer_id')['quantity_kg'].sum().reset_index(name='dealer_total_quantity')
    df = df.merge(dealer_total_qty, on='dealer_id', how='left')
    
    return df

def create_invoice_features(df):
    print("Creating invoice-derived features...")
    
    invoice_dealer_counts = df.groupby(['dealer_id', 'invoice_no']).size().reset_index(name='count')
    invoice_dealer_counts['invoice_duplicate_flag'] = (invoice_dealer_counts['count'] > 1).astype(int)
    invoice_dealer_counts = invoice_dealer_counts[['dealer_id', 'invoice_no', 'invoice_duplicate_flag']]
    
    df = df.merge(invoice_dealer_counts, on=['dealer_id', 'invoice_no'], how='left')
    df['invoice_duplicate_flag'] = df['invoice_duplicate_flag'].fillna(0).astype(int)
    
    return df

def create_rule_features(df):
    print("Creating rule-based features...")
    
    df['allowed_quantity'] = df['max_qty_per_ha'] * df['land_holding_ha']
    df['quantity_vs_allowed'] = df['quantity_kg'] - df['allowed_quantity']
    df['subsidy_vs_allowed'] = df['subsidy_amount'] - df['max_subsidy_amount']
    
    return df

def create_geo_features(df):
    print("Creating geo-distance features...")
    
    def compute_distance(row):
        try:
            if pd.isna(row['geo_lat']) or pd.isna(row['geo_lon']) or \
               pd.isna(row['lat']) or pd.isna(row['lon']):
                return np.nan
            farmer_coords = (row['geo_lat'], row['geo_lon'])
            dealer_coords = (row['lat'], row['lon'])
            return haversine(farmer_coords, dealer_coords)
        except:
            return np.nan
    
    df['distance_farmer_to_dealer_km'] = df.apply(compute_distance, axis=1)
    
    return df

def create_time_features(df):
    print("Creating time features...")
    
    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    
    df['txn_hour'] = pd.to_datetime(df['txn_time'], format='%H:%M:%S', errors='coerce').dt.hour
    df['txn_day'] = df['txn_date'].dt.day
    df['txn_month'] = df['txn_date'].dt.month
    
    return df

def main():
    farmers, dealers, transactions, scheme_rules = load_data()
    
    df = perform_joins(farmers, dealers, transactions, scheme_rules)
    
    df = create_farmer_features(df)
    df = create_dealer_features(df)
    df = create_invoice_features(df)
    df = create_rule_features(df)
    df = create_geo_features(df)
    df = create_time_features(df)
    
    df.to_csv(CURRENT_DIR / 'processed_features.csv', index=False)
    
    num_rows = len(df)
    num_features = len(df.columns)
    
    print(f"Feature engineering completed")
    print(f"Rows: {num_rows}")
    print(f"Features: {num_features}")

if __name__ == '__main__':
    main()
