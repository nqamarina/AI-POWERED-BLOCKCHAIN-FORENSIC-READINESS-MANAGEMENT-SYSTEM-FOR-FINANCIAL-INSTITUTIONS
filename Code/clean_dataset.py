import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import joblib

print("🔄 Step 1: Loading raw transaction dataset from absolute path...")

# 🌟 DIRECT PATH POINTER: Reaches outside your code folder to read the raw data
RAW_DATA_PATH = r"C:\Users\User\OneDrive - mmu.edu.my (1)\Desktop\FYP PAPERS\Product\Sampled Data\PS_20174392719_1491204439457_log.csv"

if not os.path.exists(RAW_DATA_PATH):
    raise FileNotFoundError(f"❌ Error: Could not find the raw file at: {RAW_DATA_PATH}\nPlease double check the filename inside the Sampled Data folder!")

# Read the large raw file directly from its destination
df = pd.read_csv(RAW_DATA_PATH)
df.columns = df.columns.str.strip()

print(f"📊 Dataset successfully loaded. Total rows parsed: {len(df):,}")

# Clean column headers to prevent processing bugs
rename_map = {}
for col in df.columns:
    if col.lower() in ['oldbalanceorig', 'oldbalanceorg']: rename_map[col] = 'oldbalanceOrig'
    if col.lower() in ['newbalanceorig', 'newbalanceorig']: rename_map[col] = 'newbalanceOrig'
    if col.lower() in ['oldbalancedest', 'oldbalancedest']: rename_map[col] = 'oldbalanceDest'
    if col.lower() in ['newbalancedest', 'newbalancedest']: rename_map[col] = 'newbalanceDest'
if rename_map:
    df = df.rename(columns=rename_map)

print("\n🔒 Step 2: Isolating identity tracking layer...")
# Extract text trackers and targets
identities_df = pd.DataFrame({
    'nameOrig': df['nameOrig'],
    'nameDest': df['nameDest'],
    'isFraud': df['isFraud']
})

# 🌟 OUTPUT PLACEMENT: Saves this right inside your active app code folder
identities_df.to_csv('Transaction_Identities.csv', index=False)
print("✅ Created identity cross-reference ledger locally: 'Transaction_Identities.csv'")

print("\n⚙️ Step 3: Executing One-Hot Encoding on categorical text attributes...")
df_encoded = pd.get_dummies(df, columns=['type'], prefix='type', dtype=float)

# Enforce schema consistency across all standard transaction categories
standard_types = ['type_CASH_IN', 'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT', 'type_TRANSFER']
for transaction_type in standard_types:
    if transaction_type not in df_encoded.columns:
        df_encoded[transaction_type] = 0.0

print("\n✂️ Step 4: Stripping non-predictive variables...")
drop_targets = ['nameOrig', 'nameDest', 'isFraud']
if 'isFlaggedFraud' in df_encoded.columns:
    drop_targets.append('isFlaggedFraud')

ai_features_raw = df_encoded.drop(columns=drop_targets)

print("\n📐 Step 5: Executing Min-Max Feature Scaling Normalization...")
scaler = MinMaxScaler()
scaled_matrix = scaler.fit_transform(ai_features_raw)

#SAVE THE SCALER OBJECT HERE SO YOUR LIVE APP CAN LOAD IT
joblib.dump(scaler, 'scaler.pkl') 
print("✅ Successfully exported 'scaler.pkl' for live application scaling!")

processed_features_df = pd.DataFrame(scaled_matrix, columns=ai_features_raw.columns)

print("\n💾 Step 6: Exporting model-ready feature sets...")
# 🌟 OUTPUT PLACEMENT: Saves the scaled file right here for your training script and Streamlit app
processed_features_df.to_csv('Processed_Financial_Data.csv', index=False)
print("✅ Saved AI processing features locally: 'Processed_Financial_Data.csv'")

print("\n🎉 Preprocessing pipeline successfully executed and synchronized local files!")