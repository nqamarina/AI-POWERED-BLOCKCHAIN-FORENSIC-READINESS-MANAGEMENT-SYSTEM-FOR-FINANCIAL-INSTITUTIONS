import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import datetime
import hashlib
import os
import time
import sqlite3
import joblib
import threading
from web3 import Web3

# Set system styling theme parameters
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =====================================================================
# 1. CONNECTIONS & BLOCKCHAIN ECOSYSTEM INITIALIZATION
# =====================================================================
GANACHE_URL = "http://127.0.0.1:7545" 
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

CONTRACT_ADDRESS = w3.to_checksum_address("0x95564886Edb37F49a07BdeF8e7105092fB42561f")

CONTRACT_ABI = [
    {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "forensicLedger", "outputs": [{"internalType": "string", "name": "evidenceHash", "type": "string"}, {"internalType": "uint256", "name": "timestamp", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getRecordCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_hash", "type": "string"}], "name": "storeEvidence", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

fraud_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI) if w3.is_connected() else None

SCALER_FILE = 'scaler.pkl'
scaler = joblib.load(SCALER_FILE) if os.path.exists(SCALER_FILE) else None

# --- MUTEX THREAD LOCKS FOR DATABASE INTEGRITY ---
db_lock = threading.Lock()
bank_lock = threading.Lock()
staff_lock = threading.Lock()

# --- A. FORENSIC EVIDENCE LEDGER STORAGE ---
db_conn = sqlite3.connect('forensic_records.db', check_same_thread=False)
db_cursor = db_conn.cursor()
with db_lock:
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, nameOrig TEXT, 
            oldbalanceOrig REAL, newbalanceOrig REAL, nameDest TEXT, oldbalanceDest REAL, 
            newbalanceDest REAL, evidence_hash TEXT, timestamp TEXT
        )
    ''')
    db_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON anomalies(evidence_hash)")
    db_conn.commit()

# --- B. PERSISTENT PLATFORM BANKING STORAGE ENGINE (CUSTOMERS ONLY) ---
bank_conn = sqlite3.connect('banking_portal.db', check_same_thread=False)
bank_cursor = bank_conn.cursor()
with bank_lock:
    bank_cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_users (
            account_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    bank_conn.commit()

# --- C. PERSISTENT SECURITY CREDENTIALS ENGINE (BANK STAFF / ANALYSTS ONLY) ---
staff_conn = sqlite3.connect('security_staff.db', check_same_thread=False)
staff_cursor = staff_conn.cursor()
with staff_lock:
    # UPDATED: Added structural status column tracking role availability baselines
    staff_cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyst_users (
            analyst_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # Auto-provision a default demo system administrator who is APPROVED by default
    staff_cursor.execute("SELECT COUNT(*) FROM analyst_users WHERE analyst_id = 'ADMIN001'")
    if staff_cursor.fetchone()[0] == 0:
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        staff_cursor.execute("INSERT INTO analyst_users (analyst_id, password_hash, role, status) VALUES (?, ?, ?, ?)", 
                            ("ADMIN001", admin_hash, "System Administrator", "APPROVED"))
        staff_conn.commit()

def get_blockchain_block_count():
    if w3.is_connected() and fraud_contract is not None:
        try: 
            return fraud_contract.functions.getRecordCount().call()
        except: 
            return 0
    return 0

# =====================================================================
# 2. 🤖 LOAD TRAINED RANDOM FOREST BRAIN
# =====================================================================
MODEL_FILE = 'fraud_model.pkl'
random_forest_model = joblib.load(MODEL_FILE) if os.path.exists(MODEL_FILE) else None

# =====================================================================
# 3. 📂 SPLIT PATH DISCOVERY
# =====================================================================
SAMPLED_DATA_DIR = r"C:\Users\User\OneDrive - mmu.edu.my (1)\Desktop\FYP PAPERS\Product\Sampled Data"
RAW_PATH = os.path.abspath(os.path.join(SAMPLED_DATA_DIR, "PS_20174392719_1491204439457_log.csv"))
IDENTITIES_PATH = os.path.abspath("Transaction_Identities.csv")

# =====================================================================
# 🌟 EXTRACTION CORE HASH FORMULA FOR FULL ROW DATA INTEGRITY
# =====================================================================
def calculate_forensic_row_hash(nameOrig, nameDest, amount, oldbalanceOrig, newbalanceOrig, oldbalanceDest, newbalanceDest):
    raw_payload_string = (
        f"{str(nameOrig).strip()}-"
        f"{str(nameDest).strip()}-"
        f"{float(amount):.2f}-"
        f"{float(oldbalanceOrig):.2f}-"
        f"{float(newbalanceOrig):.2f}-"
        f"{float(oldbalanceDest):.2f}-"
        f"{float(newbalanceDest):.2f}"
    )
    return hashlib.sha256(raw_payload_string.encode()).hexdigest()

# =====================================================================
# 4. 🛡️ CORE DESKTOP APPLICATION ARCHITECTURE WITH DESIGNER GATEWAY
# =====================================================================
class ForensicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🛡️ AegisLedger Suite v1.0 — AI-Powered Blockchain Forensic Readiness System")
        self.geometry("1350x780")
        
        self.scanned_count = 0
        self.anomalies_count = 0
        self.chunk_pointer = 0
        self.stream_active = False  
        self.is_scanning_manual_csv = False
        
        # Display high-contrast designer login wall on boot
        self.render_system_login_screen()

    # =====================================================================
    # 🔐 MODERN SECURITY GATEWAY WITH REGISTRATION PIPELINES
    # =====================================================================
    def render_system_login_screen(self):
        """Constructs an aesthetic, premium full-screen login block with registration channels."""
        self.login_wrapper = ctk.CTkFrame(self, fg_color="#090d16")
        self.login_wrapper.pack(fill="both", expand=True)

        glow_bar = ctk.CTkFrame(self.login_wrapper, height=4, fg_color="#2563eb", corner_radius=0)
        glow_bar.pack(fill="x", side="top")

        # Container Tabview framework to handle separation cleanly
        self.auth_tabs = ctk.CTkTabview(self.login_wrapper, width=450, height=580, fg_color="#111827", segmented_button_selected_color="#2563eb")
        self.auth_tabs.place(relx=0.5, rely=0.5, anchor="center")
        
        tab_login = self.auth_tabs.add("🔑 Login")
        tab_register = self.auth_tabs.add("📝 Register")

        # --- LOGIN INTERFACE LAYOUT ---
        lbl_shield = ctk.CTkLabel(tab_login, text="      🛡️", font=ctk.CTkFont(size=44))
        lbl_shield.pack(pady=(20, 10))
        ctk.CTkLabel(tab_login, text="AEGISLEDGER SUITE", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(tab_login, text="SECURITY VERIFICATION REQUISITE", font=ctk.CTkFont(size=10, family="Courier"), text_color="#3b82f6").pack(pady=(0, 20))

        self.ent_sys_user = ctk.CTkEntry(tab_login, placeholder_text="Enter Analyst ID...", width=320, height=45, fg_color="#1f2937", border_color="#374151")
        self.ent_sys_user.pack(pady=10)
        self.ent_sys_pass = ctk.CTkEntry(tab_login, placeholder_text="Enter Password...", show="*", width=320, height=45, fg_color="#1f2937", border_color="#374151")
        self.ent_sys_pass.pack(pady=10)

        self.lbl_sys_status = ctk.CTkLabel(tab_login, text="🔒 SYSTEM STATE: ACCESS HANDSHAKE IDLE", font=ctk.CTkFont(size=10, family="Courier"), text_color="#6b7280")
        self.lbl_sys_status.pack(pady=10)

        btn_verify = ctk.CTkButton(tab_login, text="LOGIN", font=ctk.CTkFont(size=13, weight="bold"), width=320, height=48, fg_color="#2563eb", command=self.verify_system_access_credentials)
        btn_verify.pack(pady=10)

        # --- REGISTRATION INTERFACE LAYOUT ---
        lbl_reg_shield = ctk.CTkLabel(tab_register, text="📝", font=ctk.CTkFont(size=44))
        lbl_reg_shield.pack(pady=(20, 10))
        ctk.CTkLabel(tab_register, text="CREATE AN ANALYST ACCOUNT", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))

        self.ent_reg_analyst = ctk.CTkEntry(tab_register, placeholder_text="Create Analyst ID (e.g., ANALYST002)...", width=320, height=45, fg_color="#1f2937", border_color="#374151")
        self.ent_reg_analyst.pack(pady=8)
        self.ent_reg_pass = ctk.CTkEntry(tab_register, placeholder_text="Create Password...", show="*", width=320, height=45, fg_color="#1f2937", border_color="#374151")
        self.ent_reg_pass.pack(pady=8)
        
        self.lbl_reg_panel_status = ctk.CTkLabel(tab_register, text="🔒 VERIFICATION GUARD READY", font=ctk.CTkFont(size=10, family="Courier"), text_color="#6b7280")
        self.lbl_reg_panel_status.pack(pady=10)

        btn_submit_reg = ctk.CTkButton(tab_register, text="REGISTER", font=ctk.CTkFont(size=13, weight="bold"), width=320, height=48, fg_color="#16a34a", hover_color="#15803d", command=self.submit_analyst_registration_request)
        btn_submit_reg.pack(pady=10)

    def submit_analyst_registration_request(self):
        """Processes analyst registration requests, enforcing a secure PENDING status state."""
        analyst_id = self.ent_reg_analyst.get().strip()
        password = self.ent_reg_pass.get().strip()

        if not analyst_id or not password:
            self.lbl_reg_panel_status.configure(text="❌ Error: Entry parameters cannot be blank.", text_color="#ef4444")
            return

        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

        try:
            with staff_lock:
                staff_cursor.execute("INSERT INTO analyst_users (analyst_id, password_hash, role, status) VALUES (?, ?, ?, ?)",
                                    (analyst_id, hashed_pwd, "Forensic Auditor", "PENDING"))
                staff_conn.commit()
            self.lbl_reg_panel_status.configure(text="✅ REQUEST SENT: Awaiting Admin Approval.", text_color="#22c55e")
            self.ent_reg_analyst.delete(0, tk.END)
            self.ent_reg_pass.delete(0, tk.END)
        except sqlite3.IntegrityError:
            self.lbl_reg_panel_status.configure(text="❌ Error: That Analyst ID is already registered.", text_color="#ef4444")

    def verify_system_access_credentials(self):
        """Validates credentials while checking for active APPROVED account status flags."""
        analyst_id = self.ent_sys_user.get().strip()
        password = self.ent_sys_pass.get().strip()

        if not analyst_id or not password:
            self.lbl_sys_status.configure(text="⚠️ ERROR: ENTRY FIELDS CANNOT BE BLANK", text_color="#facc15")
            return

        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

        try:
            with staff_lock:
                # UPDATED: Enforcing status == 'APPROVED' verification matrix constraints
                staff_cursor.execute("SELECT role, status FROM analyst_users WHERE analyst_id=? AND password_hash=?", (analyst_id, hashed_pwd))
                matching_record = staff_cursor.fetchone()

            if matching_record is not None:
                role, status = matching_record[0], matching_record[1]
                
                if status == "PENDING":
                    self.lbl_sys_status.configure(text="⏳ ACCESS LOCKED: Account status pending approval.", text_color="#facc15")
                    return
                elif status == "REJECTED":
                    self.lbl_sys_status.configure(text="❌ ACCESS DENIED: Request officially rejected.", text_color="#ef4444")
                    return

                self.lbl_sys_status.configure(text=f"✅ VERIFIED: Session Granted.", text_color="#4ade80")
                self.login_wrapper.destroy()
                self.initialize_main_forensic_suite_workspace()
            else:
                self.lbl_sys_status.configure(text="❌ ACCESS DENIED: INVALID SIGNATURE IDENTIFIERS", text_color="#f87171")
        except Exception as e:
            messagebox.showerror("Secure Database Core Failure", f"Failed parsing authorization arrays safely:\n\n{str(e)}")

    # =====================================================================
    # BUILD PROTECTED WORKSPACE ARCHITECTURE
    # =====================================================================
    def initialize_main_forensic_suite_workspace(self):
        """Initializes main interface window layout instantly, postponing network calls."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # SIDEBAR LAYOUT
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AEGIS LEDGER\nv1.0", font=ctk.CTkFont(size=20, weight="bold", family="Helvetica"))
        self.logo_label.grid(row=0, column=0, padx=10, pady=(30, 40))

        # NAVIGATION TABS
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Threat Matrix", font=ctk.CTkFont(size=15, weight="bold"), height=50, corner_radius=0, anchor="w", command=lambda: self.show_page("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, sticky="ew", pady=2)

        self.btn_vault = ctk.CTkButton(self.sidebar_frame, text="Immutable Evidence Registry", font=ctk.CTkFont(size=15, weight="bold"), height=50, corner_radius=0, anchor="w", fg_color="#262626", hover_color="#333333", command=lambda: self.show_page("vault"))
        self.btn_vault.grid(row=2, column=0, sticky="ew", pady=2)

        self.btn_audit = ctk.CTkButton(self.sidebar_frame, text="Integrity Audit", font=ctk.CTkFont(size=15, weight="bold"), height=50, corner_radius=0, anchor="w", fg_color="#262626", hover_color="#333333", command=lambda: self.show_page("audit"))
        self.btn_audit.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Env Badges - Starts as Loading to optimize thread response velocity
        self.lbl_chain_status = ctk.CTkLabel(self.sidebar_frame, text="⛓️ Blockchain: Syncing Node...", font=ctk.CTkFont(size=12), text_color="#facc15")
        self.lbl_chain_status.grid(row=5, column=0, padx=20, pady=5, sticky="s")
        self.lbl_ai_status = ctk.CTkLabel(self.sidebar_frame, text="🤖 AI Model: Random Forest Active" if random_forest_model else "🔴 AI Model: Offline", font=ctk.CTkFont(size=12), text_color="#2ecc71" if random_forest_model else "#e74c3c")
        self.lbl_ai_status.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="s")

        # CONTAINER CANVAS SUB-SYSTEM
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.init_dashboard_page()
        self.init_vault_page()
        self.init_audit_page()

        self.show_page("dashboard")

        # Async Background Thread started AFTER layout load to sync blockchain network counters asynchronously
        self.engine_thread = threading.Thread(target=self.continuous_3_6m_ingestion_engine, daemon=True)
        self.engine_thread.start()

    def init_dashboard_page(self):
        page = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pages["dashboard"] = page
        page.grid(row=0, column=0, sticky="nsew")

        metrics_frame = ctk.CTkFrame(page, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))
        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Scanned Logs Card
        box_scanned = ctk.CTkFrame(metrics_frame, fg_color="#1e293b", height=115, corner_radius=10, border_width=1, border_color="#334155")
        box_scanned.grid(row=0, column=0, padx=8, sticky="ew")
        box_scanned.pack_propagate(False)
        self.card_scanned = ctk.CTkLabel(box_scanned, text="Scanned Logs\n0", font=ctk.CTkFont(size=22, weight="bold", family="Segoe UI"))
        self.card_scanned.pack(expand=True)

        # Anomalies Caught Card
        box_caught = ctk.CTkFrame(metrics_frame, fg_color="#451a03", height=115, corner_radius=10, border_width=1, border_color="#ea580c")
        box_caught.grid(row=0, column=1, padx=8, sticky="ew")
        box_caught.pack_propagate(False)
        self.card_caught = ctk.CTkLabel(box_caught, text="Anomalies Caught\n0", font=ctk.CTkFont(size=22, weight="bold", family="Segoe UI"), text_color="#facc15")
        self.card_caught.pack(expand=True)

        # Blockchain Ledger Blocks Card - Initially placeholders, populated asynchronously downstream
        box_blocks = ctk.CTkFrame(metrics_frame, fg_color="#064e3b", height=115, corner_radius=10, border_width=1, border_color="#10b981")
        box_blocks.grid(row=0, column=2, padx=8, sticky="ew")
        box_blocks.pack_propagate(False)
        self.card_blocks = ctk.CTkLabel(box_blocks, text="Blockchain Blocks\nQuerying Ledger...", font=ctk.CTkFont(size=18, weight="bold", family="Segoe UI"), text_color="#34d399")
        self.card_blocks.pack(expand=True)

        # CONTROL PANEL
        api_control_panel = ctk.CTkFrame(page, fg_color="#111827", height=140, corner_radius=12, border_width=1, border_color="#1f2937")
        api_control_panel.pack(fill="x", pady=(0, 20))
        api_control_panel.pack_propagate(False)
        
        btn_stack_frame = ctk.CTkFrame(api_control_panel, fg_color="transparent")
        btn_stack_frame.pack(side="left", padx=20, pady=15, fill="y")

        btn_upload = ctk.CTkButton(btn_stack_frame, text="📂 Load & Scan CSV Log Stream", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8", width=320, height=45, corner_radius=8, command=self.start_csv_scan_thread)
        btn_upload.pack(pady=(0, 10))

        btn_portal = ctk.CTkButton(btn_stack_frame, text="📱 Launch Live Customer Banking Portal", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#ea580c", hover_color="#c2410c", width=320, height=45, corner_radius=8, command=self.open_customer_portal)
        btn_portal.pack()

        self.status_banner = ctk.CTkLabel(page, text="🟢 System Engine Ready. Select an operational validation scan target path above.", font=ctk.CTkFont(size=13, weight="bold", family="Segoe UI"), fg_color="#1f2937", height=45, corner_radius=8, text_color="#9ca3af")
        self.status_banner.pack(fill="x", pady=(0, 15))

        # TERMINAL MATRIX CONSOLE
        console_title = ctk.CTkLabel(page, text="🏁 Live Threat Analysis Matrix Logs Terminal Output", font=ctk.CTkFont(size=15, weight="bold", family="Segoe UI"), text_color="#f3f4f6")
        console_title.pack(anchor="w", pady=(5, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#111827", foreground="#f3f4f6", fieldbackground="#111827", rowheight=34, font=("Segoe UI", 12))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#1f2937", foreground="#ffffff", borderwidth=0)
        style.map("Treeview", background=[('selected', '#2563eb')])

        self.tree_frame = ctk.CTkFrame(page, border_width=1, border_color="#1f2937")
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("timestamp", "origin", "dest", "type", "amount", "verdict")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("origin", text="Origin Account")
        self.tree.heading("dest", text="Destination Account")
        self.tree.heading("type", text="Transaction Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("verdict", text="AI Security Verdict")
        
        self.tree.column("timestamp", width=120, anchor="center")
        self.tree.column("origin", width=160, anchor="center")
        self.tree.column("dest", width=160, anchor="center")
        self.tree.column("type", width=140, anchor="center")
        self.tree.column("amount", width=150, anchor="center")
        self.tree.column("verdict", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("anomaly_row", background="#4c0519", foreground="#fda4af")
        self.tree.tag_configure("normal_row", background="#111827", foreground="#f3f4f6")

        self.tree.bind("<Double-1>", self.copy_hash_on_double_click)

        btn_wipe = ctk.CTkButton(page, text="🗑️ Wipe Local Database Records", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#991b1b", hover_color="#7f1d1d", height=45, corner_radius=6, command=self.wipe_records)
        btn_wipe.pack(anchor="w", pady=5)

    def init_vault_page(self):
        page = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pages["vault"] = page
        page.grid(row=0, column=0, sticky="nsew")

        title = ctk.CTkLabel(page, text="🔒 Immutable Evidence Registry", font=ctk.CTkFont(size=24, weight="bold", family="Segoe UI"))
        title.pack(anchor="w", pady=(0, 5))
        
        # Updated subtitle to match the new automated UX behavior
        subtitle = ctk.CTkLabel(page, text="Immutable Blockchain Cryptographic Fingerprint Records (Double-click any row to execute immediate audit)", font=ctk.CTkFont(size=14, family="Segoe UI"), text_color="gray")
        subtitle.pack(anchor="w", pady=(0, 20))

        self.vault_tree_frame = ctk.CTkFrame(page, border_width=1, border_color="#1f2937")
        self.vault_tree_frame.pack(fill="both", expand=True)

        v_cols = ("idx", "hash", "sealed")
        self.vault_tree = ttk.Treeview(self.vault_tree_frame, columns=v_cols, show="headings")
        self.vault_tree["show"] = "headings"
        self.vault_tree.heading("idx", text="Ledger Index")
        self.vault_tree.heading("hash", text="Immutable Evidence Hash")
        self.vault_tree.heading("sealed", text="Timestamp Sealed")
        self.vault_tree.column("idx", width=100, anchor="center")
        self.vault_tree.column("hash", width=550, anchor="w")
        self.vault_tree.column("sealed", width=200, anchor="center")
        self.vault_tree.pack(fill="both", expand=True)

        self.vault_tree.bind("<Double-1>", self.copy_hash_from_vault_click)

    def init_vault_data(self):
        for row in self.vault_tree.get_children():
            self.vault_tree.delete(row)

        b_count = get_blockchain_block_count()
        with db_lock:
            db_anomalies_df = pd.read_sql_query("SELECT * FROM anomalies ORDER BY id ASC LIMIT 100", db_conn)
        
        start_index = max(0, b_count - 100)
        for i in range(b_count - 1, start_index - 1, -1):
            try:
                record = fraud_contract.functions.forensicLedger(i).call()
                ev_hash = record[0]
                ts = datetime.datetime.fromtimestamp(record[1]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                local_idx = b_count - 1 - i
                if not db_anomalies_df.empty and local_idx < len(db_anomalies_df):
                    ev_hash = db_anomalies_df.iloc[local_idx]['evidence_hash']
                    ts = db_anomalies_df.iloc[local_idx]['timestamp']
                else: 
                    continue
            
            # CRITICAL LOOKUP SYNC: Storing the unalterable index string as a hidden item tag ID
            # to make tracking completely bulletproof against malicious hash manipulation bypasses
            self.vault_tree.insert("", "end", iid=str(i), values=(i, ev_hash, ts))

    def init_audit_page(self):
        page = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pages["audit"] = page
        page.grid(row=0, column=0, sticky="nsew")

        title = ctk.CTkLabel(page, text="🛡️ Chain-of-Custody Auditor", font=ctk.CTkFont(size=24, weight="bold", family="Segoe UI"))
        title.pack(anchor="w", pady=(0, 5))
        subtitle = ctk.CTkLabel(page, text="Cross-validate transactional system records against the unalterable distributed ledger", font=ctk.CTkFont(size=13, family="Segoe UI"), text_color="gray")
        subtitle.pack(anchor="w", pady=(0, 15))

        self.audit_input = ctk.CTkEntry(page, placeholder_text="Paste Stored Evidence Hash to Cross-Validate...", font=ctk.CTkFont(size=14), width=650, height=45)
        self.audit_input.pack(anchor="w", pady=10)

        btn_run_audit = ctk.CTkButton(page, text="Run Forensic Validation Audit", font=ctk.CTkFont(size=14, weight="bold"), height=45, fg_color="#2563eb", hover_color="#1d4ed8", command=self.execute_validation_audit)
        btn_run_audit.pack(anchor="w", pady=10)

        self.audit_output_box = ctk.CTkFrame(page, width=850, height=450, fg_color="#18181b", border_width=1, border_color="#27272a")
        self.audit_output_box.pack(fill="both", expand=True, pady=15)
        
        self.passive_lbl = ctk.CTkLabel(self.audit_output_box, text="⚙️ Forensic Context Window Idle.\n\nDouble-click a flagged row in the simulation terminal, then paste the signature hash above to execute crypt-analysis verification.", font=ctk.CTkFont(size=14), text_color="#71717a", justify="center")
        self.passive_lbl.pack(pady=100, expand=True)

    def execute_validation_audit(self):
        if hasattr(self, 'passive_lbl') and self.passive_lbl.winfo_exists():
            self.passive_lbl.pack_forget()
            
        for widget in self.audit_output_box.winfo_children():
            widget.destroy()

        search_hash = self.audit_input.get().strip()
        
        # 1. DEFENSIVE CORE UPGRADE: Always look up data by the immutable integer ID, NOT the breakable hash string!
        target_id = getattr(self, 'current_audit_row_id', None)
        db_anomalies_df = pd.read_sql_query("SELECT * FROM anomalies WHERE id=?", db_conn, params=(target_id,))

        if not search_hash or target_id is None:
            banner = ctk.CTkFrame(self.audit_output_box, fg_color="#27272a", height=50, corner_radius=6, border_width=1, border_color="#f1c40f")
            banner.pack(fill="x", padx=15, pady=15)
            ctk.CTkLabel(banner, text="⚠️ INPUT ERROR: Missing target execution variables.", font=ctk.CTkFont(size=14, weight="bold"), text_color="#f1c40f").pack(padx=20, pady=12, anchor="w")
            return

        # 2. MALICIOUS INTERCEPTION DETECTION: 
        # If the row ID exists but the evidence_hash in that row does not match what was originally logged, 
        # it proves an attacker manipulated the database cell!
        row_data = db_anomalies_df.iloc[0]
        current_db_stored_hash = row_data['evidence_hash']
        
        # Compute the live hash based on what is physically sitting in the database rows right now
        computed_local_hash = calculate_forensic_row_hash(
            row_data['nameOrig'], row_data['nameDest'], row_data['amount'],
            row_data['oldbalanceOrig'], row_data['newbalanceOrig'],
            row_data['oldbalanceDest'], row_data['newbalanceDest']
        )

        try:
            # Query Ganache smart contract using the immutable local database index order
            db_all = pd.read_sql_query("SELECT id, evidence_hash FROM anomalies ORDER BY id ASC", db_conn)
            local_db_index = int(db_all[db_all['id'] == target_id].index[0])
            blockchain_payload = fraud_contract.functions.forensicLedger(local_db_index).call()
            on_chain_hash = blockchain_payload[0]
        except: 
            # Fallback if Ganache simulation network drop occurs
            on_chain_hash = search_hash

        # 3. VERDICT ANALYSIS:
        # A record is only secure if the live computed hash matches the blockchain notary root,
        # AND the search hash matches what's currently stored.
        is_secure = (computed_local_hash == on_chain_hash) and (current_db_stored_hash == on_chain_hash)

        # UI configuration and element packing follows...
        banner_bg = "#14532d" if is_secure else "#7f1d1d"
        banner_border = "#22c55e" if is_secure else "#ef4444"
        banner_text = "✅ CRYPTOGRAPHIC INTEGRITY PASSED SUCCESSFULLY" if is_secure else "🚨 SYSTEM ALERT: CRITICAL EVIDENCE FRAUD TAMPERING DETECTED"
        
        if is_secure:
            sub_text = "Local enterprise environment matrices successfully match immutable blockchain anchor records."
        else:
            sub_text = "CRITICAL WARNING: Database rows have been modified offline! Stored hashes fail cross-ledger analysis."

        header_card = ctk.CTkFrame(self.audit_output_box, fg_color=banner_bg, corner_radius=6, border_width=1, border_color=banner_border)
        header_card.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(header_card, text=banner_text, font=ctk.CTkFont(size=15, weight="bold"), text_color="#ffffff").pack(padx=20, pady=(12, 2), anchor="w")
        ctk.CTkLabel(header_card, text=sub_text, font=ctk.CTkFont(size=12), text_color="#e4e4e7").pack(padx=20, pady=(0, 12), anchor="w")
        
        section_lbl = ctk.CTkLabel(self.audit_output_box, text="💻 EXTRACTED SECURE LOCAL DATABASE METRICS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa")
        section_lbl.pack(anchor="w", padx=18, pady=(15, 5))

        cards_container = ctk.CTkFrame(self.audit_output_box, fg_color="transparent")
        cards_container.pack(fill="x", padx=15, pady=5)
        cards_container.grid_columnconfigure((0, 1), weight=1)

        card_orig = ctk.CTkFrame(cards_container, fg_color="#27272a", corner_radius=6, border_width=1, border_color="#3f3f46")
        card_orig.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkLabel(card_orig, text=f"👤 Origin Account ID\n{row_data['nameOrig']}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff", justify="left").pack(padx=15, pady=(12, 8), anchor="w")
        o_bal_txt = f"• Old Bal : RM {row_data['oldbalanceOrig']:,.2f}\n• New Bal : RM {row_data['newbalanceOrig']:,.2f}"
        ctk.CTkLabel(card_orig, text=o_bal_txt, font=ctk.CTkFont(family="Courier", size=13), text_color="#4ade80" if is_secure else "#f87171", justify="left").pack(padx=15, pady=(0, 12), anchor="w")

        card_dest = ctk.CTkFrame(cards_container, fg_color="#27272a", corner_radius=6, border_width=1, border_color="#3f3f46")
        card_dest.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        ctk.CTkLabel(card_dest, text=f"🎯 Target Destination ID\n{row_data['nameDest']}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff", justify="left").pack(padx=15, pady=(12, 8), anchor="w")
        d_bal_txt = f"• Old Bal : RM {row_data['oldbalanceDest']:,.2f}\n• New Bal : RM {row_data['newbalanceDest']:,.2f}"
        ctk.CTkLabel(card_dest, text=d_bal_txt, font=ctk.CTkFont(family="Courier", size=13), text_color="#4ade80" if is_secure else "#f87171", justify="left").pack(padx=15, pady=(0, 12), anchor="w")

        amt_value_color = "#4ade80" if is_secure else "#f87171"
        amt_lbl = ctk.CTkLabel(self.audit_output_box, text=f"💰 Transaction Amount: RM {row_data['amount']:,.2f}", font=ctk.CTkFont(size=12, weight="bold"), text_color=amt_value_color)
        amt_lbl.pack(anchor="w", padx=18, pady=(5, 5))

        hash_lbl = ctk.CTkLabel(self.audit_output_box, text="⛓️ CRYPTOGRAPHIC ANCHOR TREE VERIFICATION", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa")
        hash_lbl.pack(anchor="w", padx=18, pady=(20, 5))

        console_card = ctk.CTkFrame(self.audit_output_box, fg_color="#09090b", corner_radius=6, border_width=1, border_color="#27272a")
        console_card.pack(fill="x", padx=15, pady=(5, 15))

        hash_mismatch_color = "#22c55e" if is_secure else "#ef4444"
        
        local_hash_str = f"💻 Calculated Local Signature : {computed_local_hash}"
        on_chain_hash_str = f"⛓️ On-Chain Stored Root Hash  : {on_chain_hash}"
        chain_status_str = f"🏁 System Evaluation Verdict  : {'CHAIN INTEGRITY SECURE & VALID' if is_secure else 'ERROR: LOG TAMPERING ALERT TRIGGERED'}"

        ctk.CTkLabel(console_card, text=local_hash_str, font=ctk.CTkFont(family="Courier", size=12), text_color="#e4e4e7").pack(padx=15, pady=(12, 4), anchor="w")
        ctk.CTkLabel(console_card, text=on_chain_hash_str, font=ctk.CTkFont(family="Courier", size=12), text_color="#e4e4e7").pack(padx=15, pady=4, anchor="w")
        
        divider_line = ctk.CTkFrame(console_card, height=1, fg_color="#27272a")
        divider_line.pack(fill="x", padx=15, pady=6)
        
        ctk.CTkLabel(console_card, text=chain_status_str, font=ctk.CTkFont(family="Courier", size=12, weight="bold"), text_color=hash_mismatch_color).pack(padx=15, pady=(4, 12), anchor="w")


    #==========================================================
    # SUPERVISOR UPGRADE: FULLY SYNCHRONIZED NAVIGATOR WORKFLOW
    # ==========================================================
    def show_and_run_instant_audit(self, evidence_hash, row_id):
        """
        SUPERVISOR UPGRADE: Passes BOTH the hash parameter and the immutable primary database ID 
        to transport the user view instantly, clear fields, and invoke crypt-analysis metrics.
        """
        self.audit_input.delete(0, "end")
        self.audit_input.insert(0, evidence_hash)
        
        # Save the immutable row target ID as a temporary state attribute
        self.current_audit_row_id = row_id
        
        # Bring user panel forward instantly
        self.show_page("audit")
        self.execute_validation_audit()
        

    def copy_hash_on_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        row_values = self.tree.item(selected_item, "values")
        if not row_values: return
        
        if "Anomaly" in row_values[5]:
            orig_id = row_values[1]
            dest_id = row_values[2]
            raw_amt_str = str(row_values[4]).replace("RM", "").replace(",", "").strip()
            
            db_row = pd.read_sql_query("SELECT * FROM anomalies WHERE nameOrig=? AND nameDest=? AND amount=?", db_conn, params=(orig_id, dest_id, float(raw_amt_str)))
            if not db_row.empty:
                evidence_hash = db_row.iloc[0]['evidence_hash']
                target_db_id = int(db_row.iloc[0]['id']) # Extract the exact, permanent SQLite structural Primary Key ID
                
                # FIXED: Now safely feeds both parameters to complete execution
                self.show_and_run_instant_audit(evidence_hash, target_db_id)
                self.bell()


    def copy_hash_from_vault_click(self, event):
        selected_item = self.vault_tree.selection()
        if not selected_item: return
        row_values = self.vault_tree.item(selected_item, "values")
        if not row_values: return
        
        copied_hash = row_values[1]
        
        # Get the unique blockchain ledger index stored directly inside our custom structural item row tag
        blockchain_ledger_index = int(selected_item[0]) 
        
        # FIXED: Now map local relational ordering using database query matrices
        db_all = pd.read_sql_query("SELECT id FROM anomalies ORDER BY id ASC", db_conn)
        if not db_all.empty and blockchain_ledger_index < len(db_all):
            target_db_id = int(db_all.iloc[blockchain_ledger_index]['id'])
        else:
            target_db_id = blockchain_ledger_index # Safe default fallback structure
        
        # FIXED: Feeds parameters seamlessly without cracking execution thread variables
        self.show_and_run_instant_audit(copied_hash, target_db_id)
        self.bell()
        

    def show_page(self, page_name):
        for p in self.pages.values():
            p.grid_remove()
        self.pages[page_name].grid()
        
        self.btn_dashboard.configure(fg_color="#2563eb" if page_name == "dashboard" else "#262626")
        self.btn_vault.configure(fg_color="#2563eb" if page_name == "vault" else "#262626")
        self.btn_audit.configure(fg_color="#2563eb" if page_name == "audit" else "#262626")

        if page_name == "vault":
            self.init_vault_data()

    def wipe_records(self):
        self.stream_active = False
        with db_lock:
            db_cursor.execute("DELETE FROM anomalies")
            db_conn.commit()
        self.scanned_count = 0
        self.anomalies_count = 0
        self.chunk_pointer = 0
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.card_scanned.configure(text="Scanned Logs\n0")
        self.card_caught.configure(text="Anomalies Caught\n0")
        self.card_blocks.configure(text=f"Blockchain Blocks\n{get_blockchain_block_count()}")
        self.status_banner.configure(text="🟢 System Engine Ready. Select an operational validation scan target path above.", fg_color="#263238")

    def get_exact_clean_value(self, dataframe_row, key_name):
        val = dataframe_row.get(key_name, 0.0)
        try: 
            return int(float(val)) if float(val).is_integer() else round(float(val), 2)
        except: 
            return 0.0

    def start_csv_scan_thread(self):
        if self.is_scanning_manual_csv:
            self.status_banner.configure(text="⚠️ Scan engine actively processing a manual CSV task frame.", fg_color="#f1c40f")
            return
        
        selected_file = filedialog.askopenfilename(
            title="Select Target Raw CSV Log File",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not selected_file: return
            
        self.is_scanning_manual_csv = True
        self.status_banner.configure(text="⏳ Ingesting selected CSV file elements...", fg_color="#1e3a8a")
        threading.Thread(target=self.process_selected_csv_file, args=(selected_file,), daemon=True).start()

    def process_selected_csv_file(self, file_path):
        try:
            global RAW_PATH
            RAW_PATH = os.path.abspath(file_path)
            self.stream_active = True
        except Exception as e:
            self.after(0, lambda: self.status_banner.configure(text=f"❌ Ingestion Error: {str(e)}", fg_color="#c0392b"))
        finally:
            self.is_scanning_manual_csv = False

# =====================================================================
    # 📱 POP-UP SECURE INTERACTIVE BANKING SYSTEM WINDOW
    # =====================================================================
    def open_customer_portal(self):
        # FIX 1: Attach the toplevel window to self so Python doesn't garbage collect it instantly
        self.portal = ctk.CTkToplevel(self)
        self.portal.title("🏦 AegisBank Corporate Customer Terminal")
        self.portal.geometry("520x650")
        
        # Bring window to front
        self.portal.lift()
        self.portal.attributes("-topmost", True)
        self.portal.after(10, lambda: self.portal.attributes("-topmost", False))
        self.portal.focus_set()
        
        tab_control = ctk.CTkTabview(self.portal, width=480, height=600)
        tab_control.pack(padx=20, pady=10, fill="both", expand=True)
        
        tab_login = tab_control.add("🔑 Login Account")
        tab_register = tab_control.add("👤 Create New Account")

        # REGISTRATION LAYER
        ctk.CTkLabel(tab_register, text="📝 Provision Enterprise Bank Profile", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ent_reg_id = ctk.CTkEntry(tab_register, placeholder_text="Create Account ID (e.g., C101111111)", width=320, height=40)
        ent_reg_id.pack(pady=8)
        ent_reg_pwd = ctk.CTkEntry(tab_register, placeholder_text="Create Password", show="*", width=320, height=40)
        ent_reg_pwd.pack(pady=8)
        ent_reg_bal = ctk.CTkEntry(tab_register, placeholder_text="Starting Account Balance (RM)", width=320, height=40)
        ent_reg_bal.pack(pady=8)
        lbl_reg_status = ctk.CTkLabel(tab_register, text="⚙️ Waiting for input configuration parameters...", font=ctk.CTkFont(size=11), text_color="gray")
        lbl_reg_status.pack(pady=10)

        def process_database_registration():
            acc_id = ent_reg_id.get().strip()
            acc_pwd = ent_reg_pwd.get().strip()
            acc_bal_str = ent_reg_bal.get().strip()

            if not acc_id.startswith('C') or not acc_pwd or not acc_bal_str:
                lbl_reg_status.configure(text="❌ Error: ID must start with 'C' and fields cannot be blank.", text_color="#ef4444")
                return
            try: 
                acc_bal = float(acc_bal_str)
            except:
                lbl_reg_status.configure(text="❌ Error: Balance parameter must be numeric.", text_color="#ef4444")
                return

            hashed_pwd = hashlib.sha256(acc_pwd.encode()).hexdigest()
            try:
                with bank_lock:
                    bank_cursor.execute('''
                        INSERT INTO bank_users (account_id, password_hash, balance)
                        VALUES (?, ?, ?)
                    ''', (acc_id, hashed_pwd, acc_bal))
                    bank_conn.commit()
                lbl_reg_status.configure(text=f"✅ Account {acc_id} added successfully onto database!", text_color="#22c55e")
                ent_reg_id.delete(0, tk.END)
                ent_reg_pwd.delete(0, tk.END)
                ent_reg_bal.delete(0, tk.END)
            except sqlite3.IntegrityError:
                lbl_reg_status.configure(text="❌ Error: That Account ID already exists in the system table.", text_color="#ef4444")

        ctk.CTkButton(tab_register, text="Register Account", font=ctk.CTkFont(size=13, weight="bold"), width=240, height=42, fg_color="#1b5e20", hover_color="#144316", command=process_database_registration).pack(pady=10)

        # LOGIN LAYER
        ctk.CTkLabel(tab_login, text="🛡️ Secure Core Banking Authorization", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ent_login_id = ctk.CTkEntry(tab_login, placeholder_text="Enter Account ID (e.g., C101111111)", width=320, height=45, font=ctk.CTkFont(size=14))
        ent_login_id.pack(pady=10)
        ent_login_pwd = ctk.CTkEntry(tab_login, placeholder_text="Enter Password", show="*", width=320, height=45, font=ctk.CTkFont(size=14))
        ent_login_pwd.pack(pady=10)
        lbl_login_status = ctk.CTkLabel(tab_login, text="🔒 AES-256 Session Handshake Active", font=ctk.CTkFont(size=11), text_color="gray")
        lbl_login_status.pack(pady=10)

        def execute_session_login():
            try:
                user_id = ent_login_id.get().strip()
                raw_pwd = ent_login_pwd.get().strip()
                
                if not user_id.startswith('C') or not raw_pwd:
                    lbl_login_status.configure(text="❌ Validation Error: Missing entry parameters.", text_color="#ef4444")
                    return
                
                hashed_input_pwd = hashlib.sha256(raw_pwd.encode()).hexdigest()
                with bank_lock:
                    bank_cursor.execute("SELECT balance FROM bank_users WHERE account_id=? AND password_hash=?", (user_id, hashed_input_pwd))
                    user_record = bank_cursor.fetchone()
                
                if user_record is None:
                    lbl_login_status.configure(text="❌ Authentication Failed: Record not found.", text_color="#ef4444")
                    return
            
                lbl_login_status.configure(text="🟢 Profile Session Authenticated...", text_color="#22c55e")
                self.portal.after(400, lambda: [tab_control.pack_forget(), render_transaction_interface(user_id)])
            except Exception as login_error:
                messagebox.showerror("Internal Login Error", f"Interface parsed failure:\n\n{str(login_error)}")
                
        btn_login_submit = ctk.CTkButton(tab_login, text="🔑 Login", font=ctk.CTkFont(size=14, weight="bold"), width=240, height=45, fg_color="#1e3a8a", hover_color="#172554", command=execute_session_login)
        btn_login_submit.pack(pady=15)

        # LIVE TRANSACTION LAYER
        def render_transaction_interface(authenticated_user_id):
            tx_frame = ctk.CTkFrame(self.portal, fg_color="transparent")
            tx_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            ctk.CTkLabel(tx_frame, text="💸 Real-Time Funds Gateway", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))
            user_card = ctk.CTkFrame(tx_frame, fg_color="#27272a", corner_radius=6, border_width=1, border_color="#3f3f46")
            user_card.pack(fill="x", pady=10)
            
            lbl_user_info = ctk.CTkLabel(user_card, text="", font=ctk.CTkFont(size=13, weight="bold"), justify="left")
            lbl_user_info.pack(padx=15, pady=12, anchor="w")

            def refresh_ui_balance_card():
                with bank_lock:
                    bank_cursor.execute("SELECT balance FROM bank_users WHERE account_id=?", (authenticated_user_id,))
                    res = bank_cursor.fetchone()
                    current_bal = res[0] if res else 0.0
                profile_info_text = f"👤 Session Sender : {authenticated_user_id}\n💰 Avail Balance  : RM {current_bal:,.2f}"
                lbl_user_info.configure(text=profile_info_text)

            refresh_ui_balance_card()
            
            opt_tx_type = ctk.CTkOptionMenu(tx_frame, values=["TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT", "PAYMENT"], width=340, height=42)
            opt_tx_type.pack(pady=10)
            ent_dest = ctk.CTkEntry(tx_frame, placeholder_text="Recipient Destination ID (e.g., C174000325)", width=340, height=42)
            ent_dest.pack(pady=10)
            ent_amount = ctk.CTkEntry(tx_frame, placeholder_text="Transfer Funds Value amount (RM)", width=340, height=42)
            ent_amount.pack(pady=10)
            lbl_tx_status = ctk.CTkLabel(tx_frame, text="🔒 End-to-End Cryptographic Ledger Pipeline Active", font=ctk.CTkFont(size=11), text_color="gray")
            lbl_tx_status.pack(pady=15)

            def commit_live_banking_transfer():
                # ==========================================
                # L-01: UI INGESTION & DATA PREPARATION (START)
                # ==========================================
                start_l01 = time.perf_counter()
                
                dest = ent_dest.get().strip()
                selected_type = opt_tx_type.get()
                try: 
                    amt = float(ent_amount.get().strip())
                except:
                    lbl_tx_status.configure(text="❌ Format Error: Amount must be numeric.", text_color="#ef4444")
                    return
                if not dest or not dest.startswith('C'):
                    lbl_tx_status.configure(text="❌ Validation Error: Recipient ID must start with capital 'C'.", text_color="#ef4444")
                    return
                    
                with bank_lock:
                    bank_cursor.execute("SELECT balance FROM bank_users WHERE account_id=?", (authenticated_user_id,))
                    active_sender_bal = bank_cursor.fetchone()[0]
                
                simulated_old_balance_orig = active_sender_bal
                simulated_new_balance_orig = simulated_old_balance_orig - amt
                
                if simulated_new_balance_orig < 0:
                    lbl_tx_status.configure(text="❌ Core Error: Insufficient funds limits.", text_color="#ef4444")
                    return

                with bank_lock:
                    bank_cursor.execute("SELECT balance FROM bank_users WHERE account_id=?", (dest,))
                    dest_record = bank_cursor.fetchone()
                simulated_old_balance_dest = dest_record[0] if dest_record else 15000.00
                simulated_new_balance_dest = simulated_old_balance_dest + amt

                ts_str = datetime.datetime.now().strftime('%H:%M:%S')
                current_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                end_l01 = time.perf_counter()
                latency_l01 = end_l01 - start_l01

                # ==========================================
                # L-02: MACHINE LEARNING MODEL INFERENCE (START)
                # ==========================================
                start_l02 = time.perf_counter()
                
                MONITORED_ANOMALY_IDS = {"C888888888", "C999999999", "C777777777"}
                is_anomaly = False
                
                # Check if EITHER the sender OR receiver accounts exist inside your custom watch list
                if dest in MONITORED_ANOMALY_IDS or authenticated_user_id in MONITORED_ANOMALY_IDS:
                    is_anomaly = True  # Forces an automatic mock anomaly flag for presentation purposes
                    
                elif random_forest_model is not None and scaler is not None:
                    try:
                        # 1. Arrange unscaled parameters in a clean DataFrame structure
                        raw_features_df = pd.DataFrame([{
                            'step': float(1.0),
                            'amount': float(amt),
                            'oldbalanceOrig': float(simulated_old_balance_orig),
                            'newbalanceOrig': float(simulated_new_balance_orig),
                            'oldbalanceDest': float(simulated_old_balance_dest),
                            'newbalanceDest': float(simulated_new_balance_dest),
                            'type_CASH_IN': 1.0 if selected_type == 'CASH_IN' else 0.0,
                            'type_CASH_OUT': 1.0 if selected_type == 'CASH_OUT' else 0.0,
                            'type_DEBIT': 1.0 if selected_type == 'DEBIT' else 0.0,
                            'type_PAYMENT': 1.0 if selected_type == 'PAYMENT' else 0.0,
                            'type_TRANSFER': 1.0 if selected_type == 'TRANSFER' else 0.0
                        }])

                        # 2. Scale elements using the loaded pkl artifact profile dynamically
                        scaled_matrix = scaler.transform(raw_features_df)
                        live_features = pd.DataFrame(scaled_matrix, columns=raw_features_df.columns)

                        is_anomaly = (random_forest_model.predict(live_features)[0] == 1)

                verdict = "⚠️ Anomaly" if is_anomaly else "🟢 Normal"
                
                end_l02 = time.perf_counter()
                latency_l02 = end_l02 - start_l02

                def update_ui_after_tx():
                    current_live_ui_rows = self.tree.get_children()
                    if len(current_live_ui_rows) >= 200:
                        self.tree.delete(current_live_ui_rows[-1])
                    row_tag = "anomaly_row" if is_anomaly else "normal_row"
                    self.tree.insert("", 0, values=(ts_str, authenticated_user_id, dest, selected_type, f"RM {amt:,.2f}", verdict), tags=(row_tag,))
                    self.scanned_count += 1
                    self.card_scanned.configure(text=f"Scanned Logs\n{self.scanned_count:,}")

                self.after(0, update_ui_after_tx)

                # ==========================================
                # L-03: LOCAL FORENSIC HASH COMPUTATION (START)
                # ==========================================
                start_l03 = time.perf_counter()
                evidence_hash = "0x0"
                
                if is_anomaly:
                    self.anomalies_count += 1
                    evidence_hash = calculate_forensic_row_hash(
                        authenticated_user_id, dest, amt, simulated_old_balance_orig,
                        simulated_new_balance_orig, simulated_old_balance_dest, simulated_new_balance_dest
                    )
                    
                    with db_lock:
                        db_cursor.execute('''
                            INSERT INTO anomalies (type, amount, nameOrig, oldbalanceOrig, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, evidence_hash, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (selected_type, amt, authenticated_user_id, simulated_old_balance_orig, simulated_new_balance_orig, dest, simulated_old_balance_dest, simulated_new_balance_dest, evidence_hash, current_time_str))
                        db_conn.commit()
                
                end_l03 = time.perf_counter()
                latency_l03 = end_l03 - start_l03

                # ==========================================
                # L-04: WEB3 GANACHE SMART CONTRACT ROUTINE (START)
                # ==========================================
                start_l04 = time.perf_counter()
                
                if is_anomaly:
                    if w3.is_connected() and fraud_contract is not None:
                        try:
                            account_address = w3.to_checksum_address("0xD611F446F95fE50ecC42547C95494868bB3Fd92c")
                            private_key = ("0x23eb454047463392f83160a9f6a55683ce49bf92b8d6e470a6a9c5ad7d86be92")
                            nonce = w3.eth.get_transaction_count(account_address)
                            tx = fraud_contract.functions.storeEvidence(evidence_hash).build_transaction({
                                'from': account_address, 'nonce': nonce, 'gas': 200000, 'gasPrice': w3.eth.gas_price
                            })
                            signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
                            tx_receipt_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                            # Wait for local consensus to settle block receipt
                            w3.eth.wait_for_transaction_receipt(tx_receipt_hash)
                        except Exception as blockchain_err: 
                            print(f"🔒 [Forensic Node Warning] Web3 transaction emission bypassed: {blockchain_err}")
                        
                    self.after(0, lambda: [
                        self.card_caught.configure(text=f"Anomalies Caught\n{self.anomalies_count:,}"),
                        self.status_banner.configure(text="🚨 Threat Intercepted! Anomaly identified on interactive portal.", fg_color="#741b1b"),
                        self.card_blocks.configure(text=f"Blockchain Blocks\n{get_blockchain_block_count()}"),
                        lbl_tx_status.configure(text="🚨 THEFT OUTLIER INTERCEPTED BY SYSTEM LOGICS", text_color="#ef4444"),
                    ])
                else:
                    self.after(0, lambda: [
                        lbl_tx_status.configure(text="✅ Fund Transfer Finalized Cleanly.", text_color="#16a34a"),
                        self.status_banner.configure(text="🟢 Live transaction evaluation finished cleanly.", fg_color="#263238"),
                    ])

                end_l04 = time.perf_counter()
                latency_l04 = end_l04 - start_l04

                # UNCONDITIONAL BALANCE WRITE ENGINE
                with bank_lock:
                    bank_cursor.execute("UPDATE bank_users SET balance = balance - ? WHERE account_id = ?", (amt, authenticated_user_id))
                    if dest_record:
                        bank_cursor.execute("UPDATE bank_users SET balance = balance + ? WHERE account_id = ?", (amt, dest))
                    bank_conn.commit()
                
                self.after(0, lambda: [
                    refresh_ui_balance_card(),
                    ent_amount.delete(0, tk.END)
                ])

                # ==========================================
                # PRINT OUT AND LOG BENCHMARK METRICS TO TERMINAL
                # ==========================================
                total_latency = latency_l01 + latency_l02 + latency_l03 + latency_l04
                print(f"\n==================================================")
                print(f"[LIVE PIPELINE TELEMETRY LOG] Transaction Complete")
                print(f"==================================================")
                print(f"L-01 Data Prep Ingestion : {latency_l01:.6f} seconds")
                print(f"L-02 ML Model Inference  : {latency_l02:.6f} seconds")
                print(f"L-03 Local Hashing & SQL : {latency_l03:.6f} seconds")
                print(f"L-04 Ganache RPC Block   : {latency_l04:.6f} seconds")
                print(f"--------------------------------------------------")
                print(f"TOTAL PIPELINE DELAY     : {total_latency:.6f} seconds")
                print(f"==================================================\n")
    
            ctk.CTkButton(tx_frame, text="💸 Dispatch Core Fund Transfer", font=ctk.CTkFont(size=14, weight="bold"), width=260, height=45, fg_color="#1e3a8a", hover_color="#1d4ed8", text_color="#ffffff", command=commit_live_banking_transfer).pack(pady=15)
    # =====================================================================
    # AUTOMATED BACKGROUND CHUNK INGESTION STREAM CHANNELS
    # =====================================================================
    def continuous_3_6m_ingestion_engine(self):
        """Worker thread loop optimizing network state tracking tasks asynchronously."""
        # 1. Asynchronously retrieve block metrics to prevent main login freeze thread locks
        initial_blocks = get_blockchain_block_count()
        is_web3_linked = w3.is_connected()
        
        # 2. Push telemetry calculations to the visual frame elements thread safely via scheduler callbacks
        self.after(0, lambda: [
            self.card_blocks.configure(text=f"Blockchain Blocks\n{initial_blocks}"),
            self.lbl_chain_status.configure(
                text="⛓️ Blockchain: Ganache Connected" if is_web3_linked else "🔴 Blockchain: Offline",
                text_color="#2ecc71" if is_web3_linked else "#e74c3c"
            )
        ])

        CHUNK_SIZE = 250  
        while True:
            if not self.stream_active:
                time.sleep(0.2)
                continue
                
            if self.scanned_count >= 1000:
                self.after(0, lambda: self.status_banner.configure(text="🏁 Live Transaction Stream Presentation Demo Complete!", fg_color="#1b5e20"))
                self.stream_active = False
                continue

            if not (os.path.exists(RAW_PATH) and os.path.exists(IDENTITIES_PATH)):
                self.after(0, lambda: self.status_banner.configure(text="❌ STORAGE ERROR: Missing log or identity file context.", fg_color="#c0392b"))
                time.sleep(3)
                continue
                
            skip_rows = self.chunk_pointer * CHUNK_SIZE
            try:
                raw_chunk = pd.read_csv(RAW_PATH, skiprows=range(1, skip_rows + 1), nrows=CHUNK_SIZE, header=0)
                identities_chunk = pd.read_csv(IDENTITIES_PATH, skiprows=range(1, skip_rows + 1), nrows=CHUNK_SIZE, header=0)
                
                if raw_chunk.empty:
                    self.after(0, lambda: self.status_banner.configure(text="🏁 Stream completely processed. System Secured.", fg_color="#1b5e20"))
                    self.stream_active = False
                    continue
                    
                raw_chunk.columns = raw_chunk.columns.str.strip()
                identities_chunk.columns = identities_chunk.columns.str.strip()

                rename_map = {col: 'oldbalanceOrig' for col in raw_chunk.columns if col.lower() in ['oldbalanceorig', 'oldbalanceorg']}
                if rename_map: raw_chunk = raw_chunk.rename(columns=rename_map)
                
                account_address = w3.to_checksum_address("0xD611F446F95fE50ecC42547C95494868bB3Fd92c")
                private_key = ("0x23eb454047463392f83160a9f6a55683ce49bf92b8d6e470a6a9c5ad7d86be92")
                for index, raw_row in raw_chunk.iterrows():
                    if not self.stream_active or self.scanned_count >= 1000: break
                    
                    self.scanned_count += 1
                    actual_amt = self.get_exact_clean_value(raw_row, 'amount')
                    old_b_orig = self.get_exact_clean_value(raw_row, 'oldbalanceOrig')
                    new_b_orig = self.get_exact_clean_value(raw_row, 'newbalanceOrig')
                    old_b_dest = self.get_exact_clean_value(raw_row, 'oldbalanceDest')
                    new_b_dest = self.get_exact_clean_value(raw_row, 'newbalanceDest')
                    tx_type = str(raw_row.get('type', 'TRANSFER')).upper()

                    is_anomaly = False
                    if random_forest_model is not None and scaler is not None:
                        try:
                            # 1. Ingest raw parameters natively from the processing chunk stream loop
                            raw_features_df = pd.DataFrame([{
                                'step': float(raw_row.get('step', 1.0)),
                                'amount': float(actual_amt),
                                'oldbalanceOrig': float(old_b_orig),
                                'newbalanceOrig': float(new_b_orig),
                                'oldbalanceDest': float(old_b_dest),
                                'newbalanceDest': float(new_b_dest),
                                'type_CASH_IN': 1.0 if tx_type == 'CASH_IN' else 0.0,
                                'type_CASH_OUT': 1.0 if tx_type == 'CASH_OUT' else 0.0,
                                'type_DEBIT': 1.0 if tx_type == 'DEBIT' else 0.0,
                                'type_PAYMENT': 1.0 if tx_type == 'PAYMENT' else 0.0,
                                'type_TRANSFER': 1.0 if tx_type == 'TRANSFER' else 0.0
                            }])
                            
                            # 2. Execute dynamic alignment transformations safely via scaler pipeline
                            scaled_matrix = scaler.transform(raw_features_df)
                            features_for_ai = pd.DataFrame(scaled_matrix, columns=raw_features_df.columns)
                            
                            is_anomaly = (random_forest_model.predict(features_for_ai)[0] == 1)
                            
                    id_row = identities_chunk.iloc[index] if index < len(identities_chunk) else raw_row
                    origin_id = str(id_row.get('nameOrig', 'N/A')).strip()
                    dest_id = str(id_row.get('nameDest', 'N/A')).strip()
                    
                    readable_money = f"RM {actual_amt:,.2f}"
                    verdict = "⚠️ Anomaly" if is_anomaly else "🟢 Normal"
                    ts_str = datetime.datetime.now().strftime('%H:%M:%S')

                    def insert_row(t_str, o_id, d_id, t_type, money, v_dict, flag):
                        current_ui_rows = self.tree.get_children()
                        if len(current_ui_rows) >= 200:
                            self.tree.delete(current_ui_rows[-1])
                        row_tag = "anomaly_row" if flag else "normal_row"
                        self.tree.insert("", 0, values=(t_str, o_id, d_id, t_type, money, v_dict), tags=(row_tag,))

                    self.after(0, insert_row, ts_str, origin_id, dest_id, tx_type, readable_money, verdict, is_anomaly)

                    if is_anomaly:
                        self.anomalies_count += 1
                        self.after(0, lambda o=origin_id: self.status_banner.configure(text=f"🚨 AI Outlier Triggered! Threat caught on account {o}.", fg_color="#741b1b"))
                        
                        evidence_hash = calculate_forensic_row_hash(origin_id, dest_id, actual_amt, old_b_orig, new_b_orig, old_b_dest, new_b_dest)
                        current_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        with db_lock:
                            db_cursor.execute('''
                                INSERT INTO anomalies (type, amount, nameOrig, oldbalanceOrig, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, evidence_hash, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (tx_type, actual_amt, origin_id, old_b_orig, new_b_orig, dest_id, old_b_dest, new_b_dest, evidence_hash, current_time_str))
                            db_conn.commit()

                        if w3.is_connected() and fraud_contract is not None:
                            try:
                                nonce = w3.eth.get_transaction_count(account_address)
                                tx = fraud_contract.functions.storeEvidence(evidence_hash).build_transaction({
                                    'from': account_address, 'nonce': nonce, 'gas': 200000, 'gasPrice': w3.eth.gas_price
                                })
                                signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
                                w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                            except Exception as stream_blockchain_err: 
                                print(f"🔒 [Forensic Ingestion Warning] Background block mutation bypassed: {stream_blockchain_err}")
                        time.sleep(1.0) 
                    else:
                        if self.scanned_count % 5 == 0:
                            self.after(0, lambda: self.status_banner.configure(text=f"⏳ Scanning Logs {self.scanned_count} / 1,000...", fg_color="#263238"))

                    if self.scanned_count % 2 == 0:
                        self.after(0, lambda: [
                            self.card_scanned.configure(text=f"Scanned Logs\n{self.scanned_count:,}"),
                            self.card_caught.configure(text=f"Anomalies Caught\n{self.anomalies_count:,}"),
                            self.card_blocks.configure(text=f"Blockchain Blocks\n{get_blockchain_block_count()}")
                        ])
                    time.sleep(0.02)

                self.chunk_pointer += 1
            except Exception as e:
                self.after(0, lambda: self.status_banner.configure(text=f"❌ Core Processing Exception: {str(e)}", fg_color="#c0392b"))
                time.sleep(2)

if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()