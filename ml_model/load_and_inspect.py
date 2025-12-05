import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Configuration
REQUIRED_FILES = ['farmers.csv', 'dealers.csv', 'transactions.csv', 'scheme_rules.csv']
CURRENT_DIR = Path(__file__).parent

def check_files_exist():
    """Verify all required CSV files exist."""
    missing_files = []
    for file in REQUIRED_FILES:
        file_path = CURRENT_DIR / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"ERROR: Missing files - {', '.join(missing_files)}")
        exit(1)

def load_data():
    """Load all CSV files."""
    print("Loading CSV files...\n")
    farmers = pd.read_csv(CURRENT_DIR / 'farmers.csv')
    dealers = pd.read_csv(CURRENT_DIR / 'dealers.csv')
    transactions = pd.read_csv(CURRENT_DIR / 'transactions.csv')
    scheme_rules = pd.read_csv(CURRENT_DIR / 'scheme_rules.csv')
    return farmers, dealers, transactions, scheme_rules

def print_basic_info(df, name):
    """Print number of rows and first 3 rows."""
    print(f"{'='*60}")
    print(f"File: {name}")
    print(f"{'='*60}")
    print(f"Total rows: {len(df)}\n")
    print("First 3 rows:")
    print(df.head(3).to_string())
    print()

def print_columns_and_missing(df, name):
    """Print column names and missing value counts."""
    print(f"\nColumn info for {name}:")
    print(f"Columns: {list(df.columns)}")
    print(f"\nMissing values per column:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        print(f"  {col}: {count}")
    print()

def check_id_ranges(farmers, dealers, transactions):
    """Verify ID ranges and formats."""
    print(f"\n{'='*60}")
    print("ID Verification")
    print(f"{'='*60}\n")
    
    # Farmers
    if 'farmer_id' in farmers.columns:
        print(f"Farmers:")
        print(f"  Min farmer_id: {farmers['farmer_id'].min()}")
        print(f"  Max farmer_id: {farmers['farmer_id'].max()}")
        print(f"  Unique count: {farmers['farmer_id'].nunique()}")
        print()
    
    # Dealers
    if 'dealer_id' in dealers.columns:
        print(f"Dealers:")
        print(f"  Min dealer_id: {dealers['dealer_id'].min()}")
        print(f"  Max dealer_id: {dealers['dealer_id'].max()}")
        print(f"  Unique count: {dealers['dealer_id'].nunique()}")
        print()
    
    # Transactions
    if 'txn_id' in transactions.columns:
        print(f"Transactions:")
        print(f"  Total rows: {len(transactions)}")
        print(f"  Unique txn_id count: {transactions['txn_id'].nunique()}")
        print()

def check_join_integrity(farmers, dealers, transactions):
    """Check for unmatched IDs and cross-district cases."""
    print(f"\n{'='*60}")
    print("Join Integrity Checks")
    print(f"{'='*60}\n")
    
    # Unmatched farmer_id
    if 'farmer_id' in transactions.columns and 'farmer_id' in farmers.columns:
        unmatched_farmers = transactions[~transactions['farmer_id'].isin(farmers['farmer_id'])]
        print(f"Transactions with unmatched farmer_id:")
        print(f"  Count: {len(unmatched_farmers)}")
        if len(unmatched_farmers) > 0:
            print(f"  Sample (up to 5):")
            print(unmatched_farmers[['txn_id', 'farmer_id']].head(5).to_string(index=False))
        print()
    else:
        unmatched_farmers = pd.DataFrame()
    
    # Unmatched dealer_id
    if 'dealer_id' in transactions.columns and 'dealer_id' in dealers.columns:
        unmatched_dealers = transactions[~transactions['dealer_id'].isin(dealers['dealer_id'])]
        print(f"Transactions with unmatched dealer_id:")
        print(f"  Count: {len(unmatched_dealers)}")
        if len(unmatched_dealers) > 0:
            print(f"  Sample (up to 5):")
            print(unmatched_dealers[['txn_id', 'dealer_id']].head(5).to_string(index=False))
        print()
    else:
        unmatched_dealers = pd.DataFrame()
    
    # Cross-district cases
    if all(col in transactions.columns for col in ['farmer_id', 'dealer_id']):
        if all(col in farmers.columns for col in ['farmer_id', 'district']) and \
           all(col in dealers.columns for col in ['dealer_id', 'district']):
            
            merged = transactions.merge(farmers[['farmer_id', 'district']], 
                                       on='farmer_id', how='left', suffixes=('', '_farmer'))
            merged = merged.merge(dealers[['dealer_id', 'district']], 
                                 on='dealer_id', how='left', suffixes=('_farmer', '_dealer'))
            
            cross_district = merged[merged['district_farmer'] != merged['district_dealer']]
            print(f"Cross-district transactions (farmer district != dealer district):")
            print(f"  Count: {len(cross_district)}")
            if len(cross_district) > 0:
                print(f"  Sample (up to 5):")
                sample_cols = ['txn_id', 'farmer_id', 'dealer_id', 'district_farmer', 'district_dealer']
                print(cross_district[sample_cols].head(5).to_string(index=False))
            print()
    
    return len(unmatched_farmers), len(unmatched_dealers)

def check_value_distributions(transactions):
    """Check value distributions and proportions."""
    print(f"\n{'='*60}")
    print("Value Distribution Checks")
    print(f"{'='*60}\n")
    
    # Quantity and subsidy stats
    if 'quantity_kg' in transactions.columns:
        qty = transactions['quantity_kg'].dropna()
        print(f"Quantity (kg) statistics:")
        print(f"  Min: {qty.min()}")
        print(f"  Median: {qty.median()}")
        print(f"  Mean: {qty.mean():.2f}")
        print(f"  Max: {qty.max()}")
        print()
    
    if 'subsidy_amount' in transactions.columns:
        sub = transactions['subsidy_amount'].dropna()
        print(f"Subsidy amount statistics:")
        print(f"  Min: {sub.min()}")
        print(f"  Median: {sub.median()}")
        print(f"  Mean: {sub.mean():.2f}")
        print(f"  Max: {sub.max()}")
        print()
    
    # Claimed land area check
    if 'claimed_land_area_ha' in transactions.columns:
        zero_land = (transactions['claimed_land_area_ha'] == 0).sum()
        total = len(transactions)
        proportion = (zero_land / total) * 100 if total > 0 else 0
        print(f"Claimed land area = 0:")
        print(f"  Count: {zero_land}")
        print(f"  Proportion: {proportion:.2f}%")
        print()

def check_duplicates_and_invoices(transactions):
    """Check for duplicate invoices and invoice reuse."""
    print(f"\n{'='*60}")
    print("Duplicate/Invoice Checks")
    print(f"{'='*60}\n")
    
    # Top 10 invoice_no with highest counts
    if 'invoice_no' in transactions.columns:
        invoice_counts = transactions['invoice_no'].value_counts()
        print(f"Top 10 invoice numbers with highest reuse:")
        top_10 = invoice_counts.head(10)
        for invoice, count in top_10.items():
            print(f"  {invoice}: {count} times")
        print()
    
    # Duplicate (dealer_id, invoice_no) pairs
    if all(col in transactions.columns for col in ['dealer_id', 'invoice_no']):
        dealer_invoice_counts = transactions.groupby(['dealer_id', 'invoice_no']).size()
        duplicates = (dealer_invoice_counts > 1).sum()
        print(f"Duplicate (dealer_id, invoice_no) pairs:")
        print(f"  Count: {duplicates}")
        print()

def save_summary_csv(farmers, dealers, transactions, unmatched_farmers_count, unmatched_dealers_count):
    """Save summary diagnostics to CSV."""
    rows_per_file = {
        'farmers': len(farmers),
        'dealers': len(dealers),
        'transactions': len(transactions),
        'scheme_rules': len(transactions)  # Placeholder; adjust if needed
    }
    
    missing_counts = {
        'farmers': farmers.isnull().sum().to_dict(),
        'dealers': dealers.isnull().sum().to_dict(),
        'transactions': transactions.isnull().sum().to_dict()
    }
    
    # Invoice duplicates
    if 'invoice_no' in transactions.columns:
        invoice_counts = transactions['invoice_no'].value_counts()
        invoice_duplicates_count = (invoice_counts > 1).sum()
    else:
        invoice_duplicates_count = 0
    
    summary_data = {
        'rows_per_file': json.dumps(rows_per_file),
        'missing_counts': json.dumps(missing_counts),
        'unmatched_farmers': unmatched_farmers_count,
        'unmatched_dealers': unmatched_dealers_count,
        'invoice_duplicates_count': invoice_duplicates_count
    }
    
    summary_df = pd.DataFrame([summary_data])
    summary_df.to_csv(CURRENT_DIR / 'data_checks_summary.csv', index=False)

def main():
    """Main execution."""
    check_files_exist()
    
    farmers, dealers, transactions, scheme_rules = load_data()
    
    # Basic info
    print_basic_info(farmers, 'farmers.csv')
    print_basic_info(dealers, 'dealers.csv')
    print_basic_info(transactions, 'transactions.csv')
    print_basic_info(scheme_rules, 'scheme_rules.csv')
    
    # Columns and missing
    print_columns_and_missing(farmers, 'farmers.csv')
    print_columns_and_missing(dealers, 'dealers.csv')
    print_columns_and_missing(transactions, 'transactions.csv')
    print_columns_and_missing(scheme_rules, 'scheme_rules.csv')
    
    # ID verification
    check_id_ranges(farmers, dealers, transactions)
    
    # Join integrity
    unmatched_farmers_count, unmatched_dealers_count = check_join_integrity(farmers, dealers, transactions)
    
    # Value checks
    check_value_distributions(transactions)
    
    # Duplicates
    check_duplicates_and_invoices(transactions)
    
    # Save summary
    save_summary_csv(farmers, dealers, transactions, unmatched_farmers_count, unmatched_dealers_count)
    
    print(f"\n{'='*60}")
    print("Load & inspect completed.")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
