# 🛡️ AegisLedger Enterprise Suite v1.0

AegisLedger is an AI-Powered, Blockchain-Based Forensic Readiness Management System designed for financial institutions. The system intercepts live transaction logs, uses a Random Forest classifier to detect anomalies in real time, and cryptographically anchors evidence seals onto a private Ethereum network to guarantee absolute log integrity and non-repudiation.

---

## 📂 Project Structure & Core Files

* **`Code/main_app.py`**: The core desktop application built on a multi-threaded `CustomTkinter` GUI. It runs the threat matrix dashboard, the live interactive customer banking portal, and the cryptographic chain-of-custody audit engine.
* **`Code/admin_portal.py`**: The administrative control framework allowing system administrators to manage platform variables, view system states, and review pending analyst registration requests.
* **`Code/clean_dataset.py`**: The data preprocessing pipeline. It handles feature extraction, categorical one-hot encoding, scales features using a `MinMaxScaler`, and serializes the preprocessing profile (`scaler.pkl`).
* **`Code/model_training.py`**: The training script that fits the Random Forest classifier core over the preprocessed data matrices to generate `fraud_model.pkl`.
* **`Code/contracts/EvidenceStore.sol`**: The Solidity smart contract deployed on the local ledger network to store and cross-reference immutable forensic payload hashes.
* **`Code/Detected_Anomalies_Master_Forensic_Report.csv`**: Automated exported forensic report capturing intercepted system telemetry.
* **`Code/sampled_1000_rows.csv`**: Extracted lightweight transaction data frame used for rapid simulation testing.
* **`Code/Transaction_Identities.csv`**: Randomized lookup mapping file matching transaction indices to simulated user account variables.

---

## 🛠️ Prerequisites & System Requirements

Before running the application, ensure you have the following installed on your local machine:

1. Python 3.x
2. Ganache (to host the private Ethereum network node)

### Python Dependency Installation
Run the following command in your terminal to install all required libraries:
```bash
pip install customtkinter pandas numpy scikit-learn joblib web3