import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timezone
import os

# ─── Theme ────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ─── Path to Django's shared SQLite DB ───────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "PORTAL_DB.sqlite3")

AUTO_REFRESH_MS = 5000  # auto-refresh every 5 seconds

def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

# ══════════════════════════════════════════════════════════════
# LOGIN WINDOW
# ══════════════════════════════════════════════════════════════
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Login -- PT4")
        self.geometry("400x320")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Student Portal",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self, text="Login with your registered account",
                     text_color="gray", font=ctk.CTkFont(size=13)).pack(pady=(0, 5))

        # DB status indicator
        self.db_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.db_status.pack(pady=(0, 10))
        self.check_db_status()

        ctk.CTkLabel(self, text="Student ID").pack(anchor="w", padx=60)
        self.id_entry = ctk.CTkEntry(self, placeholder_text="e.g. 2024-0001", width=280)
        self.id_entry.pack(padx=60, pady=(0, 10))

        ctk.CTkLabel(self, text="Password").pack(anchor="w", padx=60)
        self.pw_entry = ctk.CTkEntry(self, placeholder_text="Enter password",
                                      width=280, show="*")
        self.pw_entry.pack(padx=60, pady=(0, 20))

        ctk.CTkButton(self, text="Login", width=280,
                      command=self.login).pack(padx=60)

        self.bind("<Return>", lambda e: self.login())

    def check_db_status(self):
        if os.path.exists(DB_PATH):
            self.db_status.configure(
                text="Connected to shared database",
                text_color="green")
        else:
            self.db_status.configure(
                text="Database not found -- run Django server first!",
                text_color="red")

    def login(self):
        sid = self.id_entry.get().strip()
        pwd = self.pw_entry.get().strip()

        if not sid or not pwd:
            messagebox.showerror("Error", "Student ID and Password are required!")
            return

        if not os.path.exists(DB_PATH):
            messagebox.showerror("Error",
                "Database not found!\nPlease run the Django server first:\npython manage.py runserver")
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT id, student_id, name, english_grade, math_grade, science_grade
                FROM portal_student
                WHERE student_id=? AND password=?
            """, (sid, pwd))
            row = c.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        if row:
            self.destroy()
            app = StudentDashboard(row)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid Student ID or Password!")
# ══════════════════════════════════════════════════════════════
# STUDENT DASHBOARD
# ══════════════════════════════════════════════════════════════
class StudentDashboard(ctk.CTk):
    def __init__(self, student_row):
        super().__init__()
        self.student_id_pk = student_row[0]
        self.student_id    = student_row[1]
        self.student_name  = student_row[2]
        self.english       = student_row[3]
        self.math          = student_row[4]
        self.science       = student_row[5]

        self.title(f"Student Dashboard -- {self.student_name}")
        self.geometry("720x560")
        self.resizable(False, False)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#2c3e50", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"Welcome, {self.student_name}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(header, text=f"  ID: {self.student_id}",
                     text_color="#aaa").pack(side="left")
        ctk.CTkButton(header, text="Logout", width=80,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      command=self.logout).pack(side="right", padx=15, pady=10)

        # ── Sync status bar ──────────────────────────────────
        sync_bar = ctk.CTkFrame(self, fg_color="#eaf4fb", corner_radius=0, height=28)
        sync_bar.pack(fill="x")
        sync_bar.pack_propagate(False)
        self.sync_label = ctk.CTkLabel(sync_bar,
                                        text="Auto-sync with Django database every 5 seconds",
                                        font=ctk.CTkFont(size=11), text_color="#2980b9")
        self.sync_label.pack(side="left", padx=15)
        self.last_sync_label = ctk.CTkLabel(sync_bar, text="",
                                             font=ctk.CTkFont(size=11), text_color="gray")
        self.last_sync_label.pack(side="right", padx=15)

        # ── Tabs ─────────────────────────────────────────────
        self.tabs = ctk.CTkTabview(self, width=700, height=470)
        self.tabs.pack(padx=10, pady=(5, 10))
        self.tabs.add("My Grades")
        self.tabs.add("Send Report")
        self.tabs.add("My Reports")

        self.build_grades_tab()
        self.build_report_tab()
        self.build_history_tab()

        # ── Start auto-refresh loop ───────────────────────────
        self.auto_refresh()

    # ── Auto-refresh ─────────────────────────────────────────
    def auto_refresh(self):
        self.reload_grades_from_db()
        self.refresh_history()
        now = datetime.now().strftime("%H:%M:%S")
        self.last_sync_label.configure(text=f"Last synced: {now}")
        self.after(AUTO_REFRESH_MS, self.auto_refresh)

    def reload_grades_from_db(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT english_grade, math_grade, science_grade
                FROM portal_student WHERE id=?
            """, (self.student_id_pk,))
            row = c.fetchone()
            conn.close()
            if row:
                self.english, self.math, self.science = row
                self.update_grades_display()
        except Exception:
            pass
        
    # ── Grades Tab ───────────────────────────────────────────
    def build_grades_tab(self):
        tab = self.tabs.tab("My Grades")

        ctk.CTkLabel(tab, text="Your Subjects and Grades",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(tab, text="Grades are synced from the Django web server.",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(0, 8))

        cols = ("Subject", "Grade", "Remarks")
        self.grades_tree = ttk.Treeview(tab, columns=cols, show="headings", height=4)
        for col in cols:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, anchor="center", width=200)
        self.grades_tree.pack(padx=20, pady=5, fill="x")

        self.summary_label = ctk.CTkLabel(tab, text="",
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.summary_label.pack(pady=8)

        self.update_grades_display()

    def update_grades_display(self):
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        subjects = [
            ("English",     self.english),
            ("Mathematics", self.math),
            ("Science",     self.science),
        ]
        total = 0
        for subj, grade in subjects:
            remark = "PASSED" if grade >= 75 else "FAILED"
            self.grades_tree.insert("", "end", values=(subj, f"{grade:.1f}", remark))
            total += grade

        avg = total / 3
        self.grades_tree.insert("", "end", values=(
            "-- AVERAGE --", f"{avg:.1f}",
            "PASSED" if avg >= 75 else "FAILED"
        ))
        color = "#27ae60" if avg >= 75 else "#e74c3c"
        status = "PASSED" if avg >= 75 else "FAILED"
        self.summary_label.configure(
            text=f"Overall Average: {avg:.2f}  |  Status: {status}",
            text_color=color)

    # ── Report Tab ───────────────────────────────────────────
    def build_report_tab(self):
        tab = self.tabs.tab("Send Report")

        ctk.CTkLabel(tab, text="Send a Message / Report",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(tab,
                     text="Your message will be saved to the shared database\nand visible on the Django web portal under Reports.",
                     text_color="gray", font=ctk.CTkFont(size=12),
                     justify="center").pack(pady=(0, 10))

        self.report_box = ctk.CTkTextbox(tab, width=620, height=200)
        self.report_box.pack(padx=20, pady=5)

        ctk.CTkButton(tab, text="Send Report", width=200,
                      command=self.send_report).pack(pady=10)

    def send_report(self):
        msg = self.report_box.get("1.0", "end").strip()
        if not msg:
            messagebox.showerror("Error", "Message cannot be empty!")
            return

        # Django stores DateTimeField as UTC ISO format with +00:00
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f+00:00")

        try:
            conn = get_connection()
            c = conn.cursor()

            # Verify student exists first
            c.execute("SELECT id FROM portal_student WHERE id=?", (self.student_id_pk,))
            if not c.fetchone():
                messagebox.showerror("Error", "Student not found in database!")
                conn.close()
                return

            c.execute("""
                INSERT INTO portal_report (student_id, message, date_sent)
                VALUES (?, ?, ?)
            """, (self.student_id_pk, msg, now))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success",
                "Report sent successfully!\nVisible on the Django web portal under /reports/")
            self.report_box.delete("1.0", "end")
            self.refresh_history()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send report:\n{str(e)}")

    # ── History Tab ──────────────────────────────────────────
    def build_history_tab(self):
        tab = self.tabs.tab("My Reports")

        ctk.CTkLabel(tab, text="Your Submitted Reports",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(tab, text="Auto-refreshes every 5 seconds from the shared database.",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(0, 5))

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(pady=(0, 5))
        ctk.CTkButton(btn_frame, text="Refresh Now", width=150,
                      command=self.refresh_history).pack()

        cols = ("ID", "Message", "Date Sent")
        self.history_tree = ttk.Treeview(tab, columns=cols, show="headings", height=11)
        self.history_tree.heading("ID", text="ID")
        self.history_tree.column("ID", anchor="center", width=50)
        self.history_tree.heading("Message", text="Message")
        self.history_tree.column("Message", anchor="w", width=420)
        self.history_tree.heading("Date Sent", text="Date Sent")
        self.history_tree.column("Date Sent", anchor="center", width=160)

        scroll = ttk.Scrollbar(tab, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scroll.set)
        self.history_tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=5)
        scroll.pack(side="right", fill="y", pady=5, padx=(0, 10))

        self.refresh_history()

    def refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT id, message, date_sent FROM portal_report
                WHERE student_id=? ORDER BY id DESC
            """, (self.student_id_pk,))
            for row in c.fetchall():
                self.history_tree.insert("", "end", values=row)
            conn.close()
        except Exception:
            pass

    def logout(self):
        self.destroy()
        login = LoginWindow()
        login.mainloop()
# ─── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()