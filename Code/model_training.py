import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# =====================================================================
# FIXED RAW ABSOLUTE PATH CONFIGURATION
# =====================================================================
# 🌟 FIXED: Pointing directly to your original big raw PaySim ledger filename
RAW_DATA_PATH = r"C:\Users\User\OneDrive - mmu.edu.my (1)\Desktop\FYP PAPERS\Product\Sampled Data\PS_20174392719_1491204439457_log.csv"

# =====================================================================
# 1. LOAD THE SPREADSHEET FILES
# =====================================================================
print("📂 Step 1: Loading synchronized preprocessed data features...")
X = pd.read_csv('Processed_Financial_Data.csv')

# Load labels directly from your local identity tracker file
identities_tracker = pd.read_csv('Transaction_Identities.csv')
y = identities_tracker['isFraud']

print(f"📊 Features Shape: {X.shape} | Labels Target Array Size: {y.shape}")

# =====================================================================
# 2. SPLIT TRAINING & TESTING SUB-MATRICES
# =====================================================================
print("\n✂️ Step 2: Splitting features matrix into Train and Test sets (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =====================================================================
# 3. INITIALIZE AND TRAIN LIGHTWEIGHT RANDOM FOREST
# =====================================================================
print("\n🤖 Step 3: Training the Random Forest Classifier...")
print("⏳ (Utilizing multi-core processing optimization. Please hold)...")

# n_jobs=-1 uses all CPU cores to speed up training from 20 minutes down to ~60 seconds
# max_depth=10 prevents the model from bloating, making it highly reactive for Streamlit
model = RandomForestClassifier(n_estimators=50, max_depth=10, class_weight='balanced', random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("✅ AI Model Training Complete!")

# =====================================================================
# 4. TESTING PERFORMANCE CHECK (FOR THESIS LOGS)
# =====================================================================
print("\n🧪 Step 4: Evaluating model accuracy metrics on unseen test partition...")
y_pred = model.predict(X_test)
print("\n--- RANDOM FOREST PERFORMANCE (TEST SET EVALUATION) ---")
print(classification_report(y_test, y_pred))

# =====================================================================
# 5. SCAN AND GENERATE 11-COLUMN FORENSIC REPORT
# =====================================================================
print("\n🔍 Step 5: Running full network scan to construct Forensic Master Report...")
y_all_pred = model.predict(X)

if os.path.exists(RAW_DATA_PATH):
    print("📋 Reaching out to raw OneDrive directory to pull complete original columns...")
    full_raw_df = pd.read_csv(RAW_DATA_PATH)
    full_raw_df.columns = full_raw_df.columns.str.strip()
    
    # Isolate exact locations flagged by the AI model
    flagged_indices = [i for i, x in enumerate(y_all_pred) if x == 1]
    
    # Pull the complete 11-column profile for those flagged indexes
    master_anomaly_report = full_raw_df.iloc[flagged_indices]
    master_anomaly_report.to_csv('Detected_Anomalies_Master_Forensic_Report.csv', index=False)
    
    print(f"✅ [SUCCESS] Master report compiled with full context variables!")
    print(f"Total anomalies anchored in master report: {len(master_anomaly_report):,}")
    
    # Calculate limitations for your thesis discussion
    missed_fraud_mask = (y == 1) & (y_all_pred == 0)
    missed_count = missed_fraud_mask.sum()
    print(f"⚠️ Total false negatives (Fraud missed by AI across dataset): {missed_count:,}")
else:
    print("⚠️ Warning: Could not locate raw source directory to back-reference transaction parameters.")

# =====================================================================
# 6. EXPORT ARTIFACT BRAIN
# =====================================================================
joblib.dump(model, 'fraud_model.pkl')
print("\n💾 Step 6: Trained model file exported safely as 'fraud_model.pkl'!")