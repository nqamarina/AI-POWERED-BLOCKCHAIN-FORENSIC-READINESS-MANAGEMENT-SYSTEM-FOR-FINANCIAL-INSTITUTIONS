import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import threading

# Set dark neon premium styling themes
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PremiumAdminPortal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("👑 AegisLedger Administrative Command Center")
        self.geometry("900x650")
        
        self.staff_lock = threading.Lock()
        self.staff_conn = sqlite3.connect('security_staff.db', check_same_thread=False)
        self.staff_cursor = self.staff_conn.cursor()

        # Render the secure Admin Login Wall on launch
        self.render_admin_login_screen()

    # =====================================================================
    # 🔐 SECURE ADMINISTRATIVE AUTHENTICATION GATEWAY
    # =====================================================================
    def render_admin_login_screen(self):
        """Constructs an aesthetic, premium full-screen login block protecting the admin tools."""
        self.login_wrapper = ctk.CTkFrame(self, fg_color="#090d16")
        self.login_wrapper.pack(fill="both", expand=True)

        glow_bar = ctk.CTkFrame(self.login_wrapper, height=4, fg_color="#ea580c", corner_radius=0)
        glow_bar.pack(fill="x", side="top")

        login_box = ctk.CTkFrame(self.login_wrapper, width=440, height=500, fg_color="#111827", border_width=1, border_color="#1f2937", corner_radius=16)
        login_box.place(relx=0.5, rely=0.5, anchor="center")

        lbl_shield = ctk.CTkLabel(login_box, text="👑", font=ctk.CTkFont(size=44))
        lbl_shield.pack(fill="x", pady=(45, 10))

        ctk.CTkLabel(login_box, text="AEGISLEDGER ADMIN", font=ctk.CTkFont(size=24, weight="bold", family="Segoe UI")).pack(pady=(0, 2))
        ctk.CTkLabel(login_box, text="CORE SYSTEM PRIVILEGE VERIFICATION GATEWAY", font=ctk.CTkFont(size=10, weight="bold", family="Courier"), text_color="#ea580c").pack(pady=(0, 25))

        fields_frame = ctk.CTkFrame(login_box, fg_color="transparent")
        fields_frame.pack(fill="x", padx=45)

        ctk.CTkLabel(fields_frame, text="ADMINISTRATOR ACCOUNT ID", font=ctk.CTkFont(size=11, weight="bold", family="Segoe UI"), text_color="#9ca3af").pack(anchor="w", pady=(0, 5))
        self.ent_admin_user = ctk.CTkEntry(fields_frame, placeholder_text="Enter Admin ID (e.g., ADMIN001)...", width=340, height=45, fg_color="#1f2937", border_color="#374151", corner_radius=8)
        self.ent_admin_user.pack(pady=(0, 15))

        ctk.CTkLabel(fields_frame, text="PASSWORD", font=ctk.CTkFont(size=11, weight="bold", family="Segoe UI"), text_color="#9ca3af").pack(anchor="w", pady=(0, 5))
        self.ent_admin_pass = ctk.CTkEntry(fields_frame, placeholder_text="Enter Secure Password...", show="*", width=340, height=45, fg_color="#1f2937", border_color="#374151", corner_radius=8)
        self.ent_admin_pass.pack(pady=(0, 20))

        self.lbl_admin_status = ctk.CTkLabel(login_box, text="🔒 SECURE PRIVILEGE CHECK: IDLE", font=ctk.CTkFont(size=11, family="Courier"), text_color="#6b7280")
        self.lbl_admin_status.pack(pady=(0, 15))

        btn_verify = ctk.CTkButton(login_box, text="VERIFY PRIVILEGES & ENTER", font=ctk.CTkFont(size=13, weight="bold", family="Segoe UI"), width=340, height=48, fg_color="#ea580c", hover_color="#c2410c", corner_radius=8, command=self.verify_admin_credentials)
        btn_verify.pack(pady=(0, 40))

    def verify_admin_credentials(self):
        """Strictly authenticates administrative access and filters by role."""
        admin_id = self.ent_admin_user.get().strip()
        password = self.ent_admin_pass.get().strip()

        if not admin_id or not password:
            self.lbl_admin_status.configure(text="⚠️ ERROR: ENTRY ATTRIBUTES MISSING", text_color="#facc15")
            return

        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

        try:
            with self.staff_lock:
                self.staff_cursor.execute("SELECT role FROM analyst_users WHERE analyst_id=? AND password_hash=?", (admin_id, hashed_pwd))
                record = self.staff_cursor.fetchone()

            if record is not None:
                role = record[0]
                if role == "System Administrator":
                    self.lbl_admin_status.configure(text="✅ ADMIN SESSION GRANTED", text_color="#4ade80")
                    self.login_wrapper.destroy()
                    self.initialize_premium_approval_dashboard()
                else:
                    self.lbl_admin_status.configure(text="❌ ACCESS DENIED: INSUFFICIENT SYSTEM PRIVILEGES", text_color="#f87171")
            else:
                self.lbl_admin_status.configure(text="❌ ACCESS DENIED: SECURE HANDSHAKE MISMATCH", text_color="#f87171")
        except Exception as e:
            messagebox.showerror("Database Access Failure", f"Failed verifying administrative matrix security context:\n\n{str(e)}")

    # =====================================================================
    # 👑 PREMIUM RE-DESIGNED MANAGEMENT DASHBOARD VIEW WITH DIRECTORY
    # =====================================================================
    def initialize_premium_approval_dashboard(self):
        """Constructs an aesthetic, highly premium administrative operations cockpit."""
        # Top Hero Header Panel
        header = ctk.CTkFrame(self, height=85, fg_color="#111827", border_width=1, border_color="#1f2937", corner_radius=0)
        header.pack(fill="x", side="top")
        
        lbl_title = ctk.CTkLabel(header, text="👑 CORE IDENTITY & SECURITY ACCESS OVERLAY", font=ctk.CTkFont(size=20, weight="bold", family="Segoe UI"))
        lbl_title.pack(side="left", padx=30, pady=25)
        
        self.lbl_badge = ctk.CTkLabel(header, text="● ADMiN SECURE ROOT", font=ctk.CTkFont(size=11, family="Courier", weight="bold"), text_color="#4ade80", fg_color="#14532d", corner_radius=20, height=26, width=150)
        self.lbl_badge.pack(side="right", padx=30, pady=25)

        # Tabbed Layout Separation Layer
        self.portal_tabs = ctk.CTkTabview(self, width=840, height=500, fg_color="transparent", segmented_button_selected_color="#ea580c")
        self.portal_tabs.pack(fill="both", expand=True, padx=30, pady=10)
        
        tab_approvals = self.portal_tabs.add("⏳ Pending Approvals")
        tab_directory = self.portal_tabs.add("👥 Active Analysts Account")

        # Global layout styling for Trees
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#111827", foreground="#f3f4f6", fieldbackground="#111827", rowheight=36, font=("Segoe UI", 12))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#1f2937", foreground="#ffffff", borderwidth=0)
        style.map("Treeview", background=[('selected', '#ea580c')])

        # -----------------------------------------------------------------
        # MODULE 1: PENDING APPROVALS
        # -----------------------------------------------------------------
        ctk.CTkLabel(tab_approvals, text="📋 Pending Analyst Accounts Awaiting Access Review:", font=ctk.CTkFont(size=13, weight="bold", family="Segoe UI"), text_color="#9ca3af").pack(anchor="w", pady=(10, 5))

        self.tree_frame = ctk.CTkFrame(tab_approvals, border_width=1, border_color="#1f2937")
        self.tree_frame.pack(fill="both", expand=True, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("id", "role", "status"), show="headings")
        self.tree.heading("id", text="Analyst Account ID")
        self.tree.heading("role", text="Designated Operational Role")
        self.tree.heading("status", text="Authorization Status State")
        self.tree.column("id", width=220, anchor="center")
        self.tree.column("role", width=250, anchor="center")
        self.tree.column("status", width=180, anchor="center")
        self.tree.pack(fill="both", expand=True)

        actions_bar = ctk.CTkFrame(tab_approvals, height=60, fg_color="transparent")
        actions_bar.pack(fill="x", pady=10)

        btn_approve = ctk.CTkButton(actions_bar, text="✅ Approve Analyst", fg_color="#16a34a", hover_color="#15803d", width=200, height=45, font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8, command=lambda: self.update_status("APPROVED"))
        btn_approve.pack(side="left", padx=(0, 15))

        btn_reject = ctk.CTkButton(actions_bar, text="❌ Reject Request", fg_color="#dc2626", hover_color="#b91c1c", width=200, height=45, font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8, command=lambda: self.update_status("REJECTED"))
        btn_reject.pack(side="left")

        btn_refresh = ctk.CTkButton(actions_bar, text="🔄 Refresh Matrix", fg_color="#1f2937", border_width=1, border_color="#374151", hover_color="#111827", width=150, height=45, corner_radius=8, command=self.load_pending_analysts)
        btn_refresh.pack(side="right")

        # -----------------------------------------------------------------
        # MODULE 2: ALL ACTIVE ANALYSTS DIRECTORY
        # -----------------------------------------------------------------

        self.dir_frame = ctk.CTkFrame(tab_directory, border_width=1, border_color="#1f2937")
        self.dir_frame.pack(fill="both", expand=True, pady=10)

        self.dir_tree = ttk.Treeview(self.dir_frame, columns=("id", "role", "status"), show="headings")
        self.dir_tree.heading("id", text="Analyst Account ID")
        self.dir_tree.heading("role", text="System Privilege Role")
        self.dir_tree.heading("status", text="Current Access Status")
        self.dir_tree.column("id", width=220, anchor="center")
        self.dir_tree.column("role", width=250, anchor="center")
        self.dir_tree.column("status", width=180, anchor="center")
        self.dir_tree.pack(fill="both", expand=True)

        # Highlight styles for Approved vs Rejected directory records
        self.dir_tree.tag_configure("approved_tag", background="#064e3b", foreground="#a7f3d0")
        self.dir_tree.tag_configure("rejected_tag", background="#4c0519", foreground="#fecdd3")

        dir_actions = ctk.CTkFrame(tab_directory, height=60, fg_color="transparent")
        dir_actions.pack(fill="x", pady=10)

        btn_refresh_dir = ctk.CTkButton(dir_actions, text="🔄 Refresh Directory", fg_color="#1f2937", border_width=1, border_color="#374151", hover_color="#111827", width=180, height=45, corner_radius=8, command=self.load_active_directory)
        btn_refresh_dir.pack(side="left")

        # Load initial configurations across tables
        self.load_pending_analysts()
        self.load_active_directory()

    def load_pending_analysts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            with self.staff_lock:
                self.staff_cursor.execute("SELECT analyst_id, role, status FROM analyst_users WHERE status='PENDING'")
                records = self.staff_cursor.fetchall()
            for record in records:
                self.tree.insert("", "end", values=record)
        except Exception as err:
            messagebox.showerror("Database Read Fault", f"Error querying access registers:\n\n{str(err)}")

    def load_active_directory(self):
        """Pulls all analysts out of security_staff.db whose status is officially APPROVED or REJECTED."""
        for row in self.dir_tree.get_children():
            self.dir_tree.delete(row)
        try:
            with self.staff_lock:
                # Select everything that is NOT pending to showcase complete directory mappings
                self.staff_cursor.execute("SELECT analyst_id, role, status FROM analyst_users WHERE status != 'PENDING'")
                records = self.staff_cursor.fetchall()
            for record in records:
                status_state = record[2]
                row_tag = "approved_tag" if status_state == "APPROVED" else "rejected_tag"
                self.dir_tree.insert("", "end", values=record, tags=(row_tag,))
        except Exception as err:
            messagebox.showerror("Database Read Fault", f"Error querying master registry directory:\n\n{str(err)}")

    def update_status(self, new_state):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please highlight an analyst record from the data matrix table.")
            return
        
        target_id = self.tree.item(selected_item, "values")[0]
        try:
            with self.staff_lock:
                self.staff_cursor.execute("UPDATE analyst_users SET status=? WHERE analyst_id=?", (new_state, target_id))
                self.staff_conn.commit()
            messagebox.showinfo("Success", f"Account registration request for {target_id} updated to [{new_state}].")
            
            # Synchronize both matrix layouts simultaneously post-mutation
            self.load_pending_analysts()
            self.load_active_directory()
        except Exception as err:
            messagebox.showerror("Database Execution Failure", f"Failed committing transaction boundaries:\n\n{str(err)}")

if __name__ == "__main__":
    portal = PremiumAdminPortal()
    portal.mainloop()