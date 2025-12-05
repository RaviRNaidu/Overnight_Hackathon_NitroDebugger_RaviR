"""
ML Data Processor - Batch processing and analysis of ML datasets
Processes Hackathon_Nitro datasets to generate insights and reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime

class MLDataProcessor:
    """Process and analyze ML datasets for fraud detection insights"""
    
    def __init__(self, data_dir='../Hackathon_Nitro'):
        self.data_dir = Path(data_dir)
        self.farmers = None
        self.dealers = None
        self.transactions = None
        self.scheme_rules = None
        self.processed_features = None
        
    def load_all_datasets(self):
        """Load all available datasets"""
        print("Loading datasets from Hackathon_Nitro...")
        
        try:
            self.farmers = pd.read_csv(self.data_dir / 'farmers.csv')
            print(f"✓ Farmers: {len(self.farmers)} records")
        except Exception as e:
            print(f"✗ Farmers: {str(e)}")
        
        try:
            self.dealers = pd.read_csv(self.data_dir / 'dealers.csv')
            print(f"✓ Dealers: {len(self.dealers)} records")
        except Exception as e:
            print(f"✗ Dealers: {str(e)}")
        
        try:
            self.transactions = pd.read_csv(self.data_dir / 'transactions.csv')
            print(f"✓ Transactions: {len(self.transactions)} records")
        except Exception as e:
            print(f"✗ Transactions: {str(e)}")
        
        try:
            self.scheme_rules = pd.read_csv(self.data_dir / 'scheme_rules.csv')
            print(f"✓ Scheme Rules: {len(self.scheme_rules)} records")
        except Exception as e:
            print(f"✗ Scheme Rules: {str(e)}")
        
        try:
            self.processed_features = pd.read_csv(self.data_dir / 'processed_features.csv')
            print(f"✓ Processed Features: {len(self.processed_features)} records")
        except Exception as e:
            print(f"✗ Processed Features: {str(e)}")
    
    def get_fraud_summary(self) -> Dict:
        """Get comprehensive fraud summary from transactions"""
        if self.transactions is None:
            return {"error": "Transactions data not loaded"}
        
        summary = {
            "total_transactions": len(self.transactions),
            "timestamp": datetime.now().isoformat()
        }
        
        if 'is_suspected_fraud' in self.transactions.columns:
            fraud_mask = self.transactions['is_suspected_fraud'] == True
            
            summary.update({
                "total_frauds": int(fraud_mask.sum()),
                "fraud_percentage": float(fraud_mask.sum() / len(self.transactions) * 100),
                "clean_transactions": int((~fraud_mask).sum())
            })
            
            # Fraud by product type
            if 'product_type' in self.transactions.columns:
                fraud_by_product = self.transactions[fraud_mask]['product_type'].value_counts()
                summary['fraud_by_product'] = fraud_by_product.to_dict()
            
            # Fraud by season
            if 'season' in self.transactions.columns:
                fraud_by_season = self.transactions[fraud_mask]['season'].value_counts()
                summary['fraud_by_season'] = fraud_by_season.to_dict()
            
            # Average fraud amount
            if 'subsidy_amount' in self.transactions.columns:
                summary['avg_fraud_amount'] = float(self.transactions[fraud_mask]['subsidy_amount'].mean())
                summary['total_fraud_amount'] = float(self.transactions[fraud_mask]['subsidy_amount'].sum())
        
        return summary
    
    def get_farmer_analysis(self) -> Dict:
        """Analyze farmer patterns"""
        if self.farmers is None:
            return {"error": "Farmers data not loaded"}
        
        analysis = {
            "total_farmers": len(self.farmers),
            "timestamp": datetime.now().isoformat()
        }
        
        if 'land_holding_ha' in self.farmers.columns:
            analysis.update({
                "avg_land_holding": float(self.farmers['land_holding_ha'].mean()),
                "median_land_holding": float(self.farmers['land_holding_ha'].median()),
                "max_land_holding": float(self.farmers['land_holding_ha'].max()),
                "min_land_holding": float(self.farmers['land_holding_ha'].min())
            })
        
        if 'is_ghost_farmer' in self.farmers.columns:
            ghost_count = self.farmers['is_ghost_farmer'].sum()
            analysis.update({
                "ghost_farmers": int(ghost_count),
                "ghost_percentage": float(ghost_count / len(self.farmers) * 100)
            })
        
        # Farmers by district
        if 'district' in self.farmers.columns:
            district_dist = self.farmers['district'].value_counts().head(10)
            analysis['top_districts'] = district_dist.to_dict()
        
        return analysis
    
    def get_dealer_analysis(self) -> Dict:
        """Analyze dealer patterns"""
        if self.dealers is None:
            return {"error": "Dealers data not loaded"}
        
        analysis = {
            "total_dealers": len(self.dealers),
            "timestamp": datetime.now().isoformat()
        }
        
        # Dealers by license type
        if 'license_type' in self.dealers.columns:
            license_dist = self.dealers['license_type'].value_counts()
            analysis['dealers_by_license'] = license_dist.to_dict()
        
        # Active vs inactive
        if 'is_active' in self.dealers.columns:
            active_count = self.dealers['is_active'].sum()
            analysis.update({
                "active_dealers": int(active_count),
                "inactive_dealers": int(len(self.dealers) - active_count),
                "active_percentage": float(active_count / len(self.dealers) * 100)
            })
        
        # Dealers by district
        if 'district' in self.dealers.columns:
            district_dist = self.dealers['district'].value_counts().head(10)
            analysis['top_districts'] = district_dist.to_dict()
        
        return analysis
    
    def get_transaction_trends(self) -> Dict:
        """Analyze transaction trends over time"""
        if self.transactions is None:
            return {"error": "Transactions data not loaded"}
        
        trends = {
            "total_transactions": len(self.transactions),
            "timestamp": datetime.now().isoformat()
        }
        
        # Convert transaction date
        if 'txn_date' in self.transactions.columns:
            self.transactions['txn_date'] = pd.to_datetime(self.transactions['txn_date'], errors='coerce')
            
            # Monthly trends
            monthly = self.transactions.groupby(self.transactions['txn_date'].dt.to_period('M')).size()
            trends['monthly_transactions'] = {str(k): int(v) for k, v in monthly.items()}
            
            # Recent activity
            if not self.transactions['txn_date'].isna().all():
                latest_date = self.transactions['txn_date'].max()
                trends['latest_transaction_date'] = str(latest_date)
        
        # Product type distribution
        if 'product_type' in self.transactions.columns:
            product_dist = self.transactions['product_type'].value_counts()
            trends['product_distribution'] = product_dist.to_dict()
        
        # Average transaction values
        if 'subsidy_amount' in self.transactions.columns:
            trends.update({
                "avg_subsidy_amount": float(self.transactions['subsidy_amount'].mean()),
                "total_subsidy_amount": float(self.transactions['subsidy_amount'].sum()),
                "max_subsidy_amount": float(self.transactions['subsidy_amount'].max())
            })
        
        if 'quantity_kg' in self.transactions.columns:
            trends.update({
                "avg_quantity_kg": float(self.transactions['quantity_kg'].mean()),
                "total_quantity_kg": float(self.transactions['quantity_kg'].sum())
            })
        
        return trends
    
    def get_high_risk_entities(self) -> Dict:
        """Identify high-risk farmers and dealers"""
        risks = {
            "high_risk_farmers": [],
            "high_risk_dealers": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if self.transactions is None or 'is_suspected_fraud' not in self.transactions.columns:
            return risks
        
        fraud_txns = self.transactions[self.transactions['is_suspected_fraud'] == True]
        
        # High-risk farmers (multiple fraud cases)
        if 'farmer_id' in fraud_txns.columns:
            farmer_fraud_counts = fraud_txns['farmer_id'].value_counts()
            high_risk_farmers = farmer_fraud_counts[farmer_fraud_counts >= 2]
            
            risks['high_risk_farmers'] = [
                {"farmer_id": str(farmer_id), "fraud_count": int(count)}
                for farmer_id, count in high_risk_farmers.head(20).items()
            ]
        
        # High-risk dealers
        if 'dealer_id' in fraud_txns.columns:
            dealer_fraud_counts = fraud_txns['dealer_id'].value_counts()
            high_risk_dealers = dealer_fraud_counts[dealer_fraud_counts >= 3]
            
            risks['high_risk_dealers'] = [
                {"dealer_id": str(dealer_id), "fraud_count": int(count)}
                for dealer_id, count in high_risk_dealers.head(20).items()
            ]
        
        return risks
    
    def get_scheme_compliance(self) -> Dict:
        """Analyze compliance with scheme rules"""
        if self.transactions is None or self.scheme_rules is None:
            return {"error": "Required data not loaded"}
        
        compliance = {
            "total_schemes": len(self.scheme_rules),
            "timestamp": datetime.now().isoformat()
        }
        
        # Violations by scheme
        if 'product_type' in self.transactions.columns and 'season' in self.transactions.columns:
            violations = []
            
            for _, rule in self.scheme_rules.iterrows():
                matching_txns = self.transactions[
                    (self.transactions['product_type'] == rule['product_type']) &
                    (self.transactions['season'] == rule['season'])
                ]
                
                if len(matching_txns) > 0 and 'is_suspected_fraud' in matching_txns.columns:
                    violation_count = matching_txns['is_suspected_fraud'].sum()
                    
                    violations.append({
                        "product_type": rule['product_type'],
                        "season": rule['season'],
                        "total_transactions": len(matching_txns),
                        "violations": int(violation_count),
                        "compliance_rate": float((len(matching_txns) - violation_count) / len(matching_txns) * 100)
                    })
            
            compliance['scheme_compliance'] = violations
        
        return compliance
    
    def generate_comprehensive_report(self, output_path: str = None) -> Dict:
        """Generate comprehensive analysis report"""
        self.load_all_datasets()
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "fraud_summary": self.get_fraud_summary(),
            "farmer_analysis": self.get_farmer_analysis(),
            "dealer_analysis": self.get_dealer_analysis(),
            "transaction_trends": self.get_transaction_trends(),
            "high_risk_entities": self.get_high_risk_entities(),
            "scheme_compliance": self.get_scheme_compliance()
        }
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to {output_path}")
        
        return report
    
    def export_to_csv(self, output_dir: str = './ml_output'):
        """Export processed data to CSV files for frontend"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        self.load_all_datasets()
        
        # Export summaries
        fraud_summary = self.get_fraud_summary()
        pd.DataFrame([fraud_summary]).to_csv(output_path / 'fraud_summary.csv', index=False)
        
        farmer_analysis = self.get_farmer_analysis()
        pd.DataFrame([farmer_analysis]).to_csv(output_path / 'farmer_analysis.csv', index=False)
        
        dealer_analysis = self.get_dealer_analysis()
        pd.DataFrame([dealer_analysis]).to_csv(output_path / 'dealer_analysis.csv', index=False)
        
        print(f"Exported analysis to {output_dir}")


if __name__ == "__main__":
    # Test the data processor
    processor = MLDataProcessor()
    report = processor.generate_comprehensive_report(output_path='ml_analysis_report.json')
    
    print("\n=== ML Data Analysis Report ===")
    print(json.dumps(report, indent=2, default=str))
