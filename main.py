import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from tkinter import font
import ctypes
import sqlite3
import calendar
import shutil
import os
import pandas as pd
import math
import random
import threading 

# --- IMPORTS FROM YOUR FILES ---
from operations import (
    create_table, insert_record, update_record, delete_record,
    fetch_all, fetch_by_sno, fetch_by_customer,
    get_all_customer_names
)
from bill_view import show_bill

# --- DPI AWARENESS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ================= DATABASE & SETUP =================
create_table()

DB_FILE = "prawn_accounts.db" 
found_files = [f for f in os.listdir('.') if f.endswith('.db') and "backup" not in f.lower()]
if found_files:
    DB_FILE = found_files[0]

# ================= POWER FEATURES: BACKUP & SPEED =================
def perform_safety_backup():
    if not os.path.exists(DB_FILE): return
    backup_dir = "Backups"
    if not os.path.exists(backup_dir):
        try: os.makedirs(backup_dir)
        except OSError: return
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"{DB_FILE.split('.')[0]}_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(DB_FILE, backup_path)
        files = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)], key=os.path.getmtime)
        if len(files) > 10:
            for f in files[:-10]: 
                try: os.remove(f)
                except: pass
    except Exception as e:
        print(f"Backup Warning: {e}")

def optimize_database_speed():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        row = cur.fetchone()
        if row:
            tbl = row[0]
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_customer ON {tbl}(CUSTOMER)")
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_date ON {tbl}(DATE)")
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_item ON {tbl}(ITEM)")
            conn.commit()
        conn.close()
    except Exception: pass 

perform_safety_backup()
optimize_database_speed()

# ================= GUI ROOT =================
root = tk.Tk()
root.title("Prawn Accounts Official App")
root.geometry("1920x1080")
root.grid_columnconfigure(tuple(range(11)), weight=1)

# ================= FONTS & STYLE =================
try:
    FONT_FAMILY = "SamsungOne"
    font.Font(family=FONT_FAMILY, size=8)
except Exception:
    FONT_FAMILY = "Segoe UI"

FONT_NORMAL = font.Font(family=FONT_FAMILY, size=8)
FONT_BOLD = font.Font(family=FONT_FAMILY, size=8, weight="bold")
FONT_BUTTON = font.Font(family=FONT_FAMILY, size=9, weight="bold") 
FONT_FOOTER = font.Font(family=FONT_FAMILY, size=10, weight="bold")

# Calendar Specific Fonts
FONT_CAL_HEADER = font.Font(family="Segoe UI", size=11, weight="bold") 
FONT_CAL_DAY = font.Font(family="Segoe UI", size=9) 
FONT_CAL_DATE = font.Font(family="Segoe UI", size=9) 

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", font=(FONT_FAMILY, 10), rowheight=30, borderwidth=1, relief="solid", background="white")
style.configure("Treeview.Heading", font=(FONT_FAMILY, 9, "bold"), background="#E6E6E6", foreground="black", borderwidth=1, relief="solid", padding=(6, 4))
style.map("Treeview.Heading", background=[("active", "#E6E6E6")])

# ================= MICROSOFT STYLE CALENDAR WIDGET =================
class MicrosoftCalendar(tk.Toplevel):
    def __init__(self, parent, target_entry):
        super().__init__(parent)
        self.target_entry = target_entry
        self.overrideredirect(True) 
        self.config(bg="white", highlightbackground="#cccccc", highlightthickness=1)
        self.attributes("-topmost", True)
        
        self.current_date = datetime.now()
        self.view_date = self.current_date
        
        self.build_ui()
        self.update_calendar()
        
        self.bind("<Leave>", self.start_close_timer)
        self.bind("<Enter>", self.cancel_close_timer)
        self.close_timer = None

    def build_ui(self):
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        self.lbl_month_year = tk.Label(header_frame, text="", font=FONT_CAL_HEADER, bg="white", anchor="w")
        self.lbl_month_year.pack(side="left")
        
        btn_next = tk.Label(header_frame, text="↓", font=("Segoe UI", 12), bg="white", cursor="hand2", fg="#555")
        btn_next.pack(side="right", padx=5)
        btn_next.bind("<Button-1>", lambda e: self.change_month(1))
        
        btn_prev = tk.Label(header_frame, text="↑", font=("Segoe UI", 12), bg="white", cursor="hand2", fg="#555")
        btn_prev.pack(side="right", padx=5)
        btn_prev.bind("<Button-1>", lambda e: self.change_month(-1))

        days_frame = tk.Frame(self, bg="white")
        days_frame.pack(fill="x", padx=15)
        days = ["S", "M", "T", "W", "T", "F", "S"]
        for i, day in enumerate(days):
            lbl = tk.Label(days_frame, text=day, font=FONT_CAL_DAY, bg="white", fg="#666", width=4)
            lbl.grid(row=0, column=i, pady=5)

        self.dates_frame = tk.Frame(self, bg="white")
        self.dates_frame.pack(padx=15, pady=5)
        
        footer = tk.Label(self, text="Go to Today", font=FONT_CAL_DAY, bg="white", fg="#0078D7", cursor="hand2")
        footer.pack(fill="x", pady=(5, 15))
        footer.bind("<Button-1>", self.go_today)

    def update_calendar(self):
        for widget in self.dates_frame.winfo_children():
            widget.destroy()

        self.lbl_month_year.config(text=self.view_date.strftime("%B %Y"))
        month_days = calendar.monthcalendar(self.view_date.year, self.view_date.month)
        today = datetime.now()
        is_current_month = (self.view_date.year == today.year and self.view_date.month == today.month)

        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                if day == 0: continue 
                
                bg_color = "white"
                fg_color = "black"
                if is_current_month and day == today.day:
                    bg_color = "#0078D7"
                    fg_color = "white"
                
                lbl = tk.Label(self.dates_frame, text=str(day), font=FONT_CAL_DATE, 
                               width=4, height=2, bg=bg_color, fg=fg_color, cursor="hand2")
                lbl.grid(row=r, column=c, padx=1, pady=1)
                lbl.bind("<Button-1>", lambda e, d=day: self.select_date(d))
                
                if not (is_current_month and day == today.day):
                    lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#E6E6E6"))
                    lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="white"))

    def change_month(self, step):
        new_month = self.view_date.month + step
        new_year = self.view_date.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1
        self.view_date = self.view_date.replace(year=new_year, month=new_month)
        self.update_calendar()

    def go_today(self, event):
        self.view_date = datetime.now()
        self.update_calendar()

    def select_date(self, day):
        sel_date = datetime(self.view_date.year, self.view_date.month, day)
        date_str = sel_date.strftime("%d-%m-%Y")
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, date_str)
        self.destroy()

    def start_close_timer(self, event):
        self.close_timer = self.after(300, self.destroy)

    def cancel_close_timer(self, event):
        if self.close_timer:
            self.after_cancel(self.close_timer)
            self.close_timer = None

cal_popup = None
def show_calendar(event, entry_widget):
    global cal_popup
    if cal_popup and cal_popup.winfo_exists():
        return 
    cal_popup = MicrosoftCalendar(root, entry_widget)
    x = entry_widget.winfo_rootx()
    y = entry_widget.winfo_rooty() + entry_widget.winfo_height() + 5
    cal_popup.geometry(f"+{x}+{y}")

# ================= ANIMATED BUTTON CLASS (HOVER) =================
class AnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, text_color="white", width=120, height=40):
        super().__init__(parent, width=width, height=height, bg="white", highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.text_color_normal = text_color
        self.text_color_hover = bg_color
        self.btn_w = width
        self.btn_h = height
        self.cx = width / 2
        self.cy = height / 2

        self.bg_rect = self.create_rectangle(0, 0, width, height, fill=bg_color, outline="", width=0)
        self.top_line = self.create_line(self.cx, 0, self.cx, 0, width=3, fill=bg_color, capstyle="projecting", state="hidden")
        self.bot_line = self.create_line(self.cx, height, self.cx, height, width=3, fill=bg_color, capstyle="projecting", state="hidden")
        
        self.text_id = self.create_text(self.cx, self.cy, text=text, font=FONT_BUTTON, fill=self.text_color_normal)
        self.current_scale = 1.0 
        self.target_scale = 1.0
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.config(cursor="hand2")

    def animate(self):
        diff = self.target_scale - self.current_scale
        if abs(diff) > 0.01:
            self.current_scale += diff * 0.2
            w_bg = self.btn_w * self.current_scale
            self.coords(self.bg_rect, self.cx - w_bg/2, 0, self.cx + w_bg/2, self.btn_h)
            line_scale = 1.0 - self.current_scale
            w_line = self.btn_w * line_scale
            self.coords(self.top_line, self.cx - w_line/2, 1.5, self.cx + w_line/2, 1.5)
            self.coords(self.bot_line, self.cx - w_line/2, self.btn_h-1.5, self.cx + w_line/2, self.btn_h-1.5)
            state = "normal" if w_line > 1 else "hidden"
            self.itemconfigure(self.top_line, state=state)
            self.itemconfigure(self.bot_line, state=state)
            self.after(16, self.animate)
        else:
            self.current_scale = self.target_scale

    def on_enter(self, event):
        self.target_scale = 0.0
        self.itemconfigure(self.text_id, fill=self.text_color_hover)
        self.animate()

    def on_leave(self, event):
        self.target_scale = 1.0
        self.itemconfigure(self.text_id, fill=self.text_color_normal)
        self.animate()

    def on_click(self, event):
        if self.command: self.command()

# ================= COMPLEX ANIMATED DOWNLOAD BUTTON =================
class DownloadAnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color="#2E7D32", text_color="white", width=140, height=40):
        super().__init__(parent, width=width, height=height, bg="white", highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.cx = width / 2
        self.cy = height / 2
        
        self.state = "idle" 
        
        # Background
        self.rect = self.create_rectangle(2, 2, width-2, height-2, fill=bg_color, outline=bg_color, width=0)
        
        # --- IDLE ELEMENTS ---
        self.arrow_group = []
        # Text "IMPORT" centered
        self.text_obj = self.create_text(self.cx - 10, self.cy, text="IMPORT", font=("Segoe UI", 9, "bold"), fill="white", anchor="center")
        
        # Arrow on the Right of text
        self.arrow_group.append(self.create_line(self.cx + 35, self.cy-6, self.cx + 35, self.cy+6, fill="white", width=2, capstyle="round", state="normal")) 
        self.arrow_group.append(self.create_line(self.cx + 35, self.cy+6, self.cx + 31, self.cy+2, fill="white", width=2, capstyle="round", state="normal")) 
        self.arrow_group.append(self.create_line(self.cx + 35, self.cy+6, self.cx + 39, self.cy+2, fill="white", width=2, capstyle="round", state="normal")) 
        
        # --- LOADING ELEMENT (Spinner) ---
        self.arc = self.create_arc(self.cx-12, self.cy-12, self.cx+12, self.cy+12, start=0, extent=120, outline="white", width=3, style="arc", state="hidden")
        
        # --- CHECKMARK ---
        self.tick_group = []
        self.tick_group.append(self.create_line(self.cx-8, self.cy, self.cx-2, self.cy+6, fill="white", width=3, capstyle="round", state="hidden")) 
        self.tick_group.append(self.create_line(self.cx-2, self.cy+6, self.cx+8, self.cy-6, fill="white", width=3, capstyle="round", state="hidden")) 

        self.bind("<Button-1>", self.on_click)
        self.config(cursor="hand2")
        self.angle = 0

    def on_click(self, event):
        if self.state != "idle": return
        
        # Start Animation Loop immediately
        self.start_loading()
        
        # Run Import in background so UI doesn't freeze
        if self.command:
            t = threading.Thread(target=self.run_command_wrapper)
            t.start()

    def run_command_wrapper(self):
        # This calls import_excel_data(), which now returns True/False
        result = self.command() 
        # Update UI back in main thread
        self.after(0, lambda: self.finish_loading(result))

    def start_loading(self):
        self.state = "loading"
        for item in self.arrow_group: self.itemconfigure(item, state="hidden")
        self.itemconfigure(self.text_obj, state="hidden")
        self.itemconfigure(self.arc, state="normal")
        self.animate_spin()

    def animate_spin(self):
        if self.state != "loading": return
        # Smoother: 5 degrees every 10ms
        self.angle = (self.angle - 5) % 360 
        self.itemconfigure(self.arc, start=self.angle)
        self.after(10, self.animate_spin)

    def finish_loading(self, success=True):
        if not success:
            # If cancelled or failed, go back to idle immediately
            self.reset()
            return

        self.state = "success"
        self.itemconfigure(self.arc, state="hidden")
        for item in self.tick_group: self.itemconfigure(item, state="normal")
        self.after(2000, self.reset)

    def reset(self):
        self.state = "idle"
        for item in self.tick_group: self.itemconfigure(item, state="hidden")
        self.itemconfigure(self.arc, state="hidden")
        for item in self.arrow_group: self.itemconfigure(item, state="normal")
        self.itemconfigure(self.text_obj, state="normal")

# ================= HELPERS & LOGIC =================
def to_float(v):
    try: return float(v)
    except (ValueError, TypeError): return 0.0

def clear_entries():
    for e in entries.values():
        e.config(state="normal")
        e.delete(0, tk.END)

def update_footer(records_to_sum):
    if not records_to_sum:
        status_label.config(text="VIEWING: 0 rows")
        return
    qty_sum = 0.0
    total_sum = 0.0
    adv_sum = 0.0
    amount_sum = 0.0
    for r in records_to_sum:
        try:
            qty_sum += float(r[6])
            total_sum += float(r[8])
            adv_sum += float(r[9])
            amount_sum += float(r[10])
        except (ValueError, IndexError, TypeError): pass
    status_text = (f"VIEWING: {len(records_to_sum)} rows  |  "
                   f"TOTAL QTY: {qty_sum:.2f}  |  "
                   f"SUM TOTAL: {total_sum:,.2f}  |  "
                   f"SUM ADVANCE: {adv_sum:,.2f}  |  "
                   f"SUM AMOUNT: {amount_sum:,.2f}")
    status_label.config(text=status_text)

def load_all():
    tree.delete(*tree.get_children())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    records = []
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        table_row = cur.fetchone()
        if table_row:
            real_table_name = table_row[0]
            try:
                cur.execute(f"SELECT * FROM {real_table_name} ORDER BY SNO ASC LIMIT 100")
            except Exception:
                cur.execute(f"SELECT * FROM {real_table_name} LIMIT 100")
            records = cur.fetchall()
    except Exception as e:
        print(f"Error loading: {e}")
        records = []
    finally:
        conn.close()

    if not records:
        try:
            records = fetch_all()
            if records: records = records[:100]
        except Exception: return

    for i, r in enumerate(records):
        r_list = list(r)
        if len(r_list) > 2: del r_list[2] # Remove TIME column
        tag = "even"
        if len(r_list) >= 13:
            tag = "incomplete" if r_list[12].lower() == "incomplete" else ("even" if i % 2 == 0 else "odd")
        tree.insert("", "end", values=r_list, tags=(tag,))
    
    update_footer(records)
    status_label.config(text=f"Displaying first {len(records)} records (Small to Big)")

def back_to_normal():
    clear_entries()
    entries["S.NO"].config(state="normal")
    entries["PAYMENT"].config(state="readonly")
    load_all()
    status_label.config(text="Ready")

def on_row_select(event):
    selected_items = tree.selection()
    if not selected_items:
        status_label.config(text="Ready")
        return
    last_sel = selected_items[-1]
    values = tree.item(last_sel, "values")
    mapping = {
        "S.NO":0, "DATE":1, 
        "CUSTOMER":2, "ITEM":3, "COUNT":4,
        "QUANTITY":5, "RATE":6, "TOTAL":7, "ADVANCE PAID":8, "AMOUNT":9,
        "PHONE":10, "LOCATION":11, "PAYMENT":12
    }
    for f, idx in mapping.items():
        if f in entries:
            entries[f].delete(0, tk.END)
            if idx < len(values): entries[f].insert(0, values[idx])
    entries["S.NO"].config(state="normal")
    qty_sum = 0.0
    total_sum = 0.0
    adv_sum = 0.0
    amount_sum = 0.0
    num_selected = len(selected_items)
    for item_id in selected_items:
        r = tree.item(item_id, "values")
        try:
            qty_sum += float(r[5])
            total_sum += float(r[7])
            adv_sum += float(r[8])
            amount_sum += float(r[9])
        except (ValueError, IndexError, TypeError): pass
    status_text = (f"SELECTED: {num_selected} rows  |  "
                   f"TOTAL QTY: {qty_sum:.2f}  |  "
                   f"SUM TOTAL: {total_sum:,.2f}  |  "
                   f"SUM ADVANCE: {adv_sum:,.2f}  |  "
                   f"SUM AMOUNT: {amount_sum:,.2f}")
    status_label.config(text=status_text)

# --- SEARCH & FILTER FUNCTIONS ---
def search_logic(func_name):
    tree.delete(*tree.get_children())
    val = entries["CUSTOMER"].get() if func_name == "name" else entries["S.NO"].get()
    records = []
    if func_name == "sno" and val.isdigit():
        r = fetch_by_sno(int(val))
        if r: records.append(r)
    elif func_name == "name":
        records = fetch_by_customer(val)
    for i, r in enumerate(records):
        r_list = list(r)
        if len(r_list) > 2: del r_list[2] # Remove Time
        tag = "incomplete" if r_list[12].lower() == "incomplete" else ("even" if i % 2 == 0 else "odd")
        tree.insert("", "end", values=r_list, tags=(tag,))
    update_footer(records)

def filter_by_payment():
    tree.delete(*tree.get_children())
    target_status = entries["PAYMENT"].get().strip().lower()
    if not target_status:
        load_all()
        return
    all_records = fetch_all()
    filtered = []
    if not all_records: return
    for i, r in enumerate(all_records):
        if r[13].lower() == target_status:
            r_list = list(r)
            if len(r_list) > 2: del r_list[2]
            tag = "incomplete" if r[13].lower() == "incomplete" else ("even" if i % 2 == 0 else "odd")
            tree.insert("", "end", values=r_list, tags=(tag,))
    update_footer(filtered)

def filter_by_item():
    tree.delete(*tree.get_children())
    target_item = entries["ITEM"].get().strip().lower()
    if not target_item:
        load_all()
        return
    all_records = fetch_all()
    filtered = []
    if not all_records: return
    for i, r in enumerate(all_records):
        if target_item in r[4].lower():
            r_list = list(r)
            if len(r_list) > 2: del r_list[2]
            tag = "incomplete" if r[13].lower() == "incomplete" else ("even" if i % 2 == 0 else "odd")
            tree.insert("", "end", values=r_list, tags=(tag,))
    update_footer(filtered)

def view_bill():
    sno = entries["S.NO"].get()
    if sno.isdigit():
        record = fetch_by_sno(int(sno))
        if record: show_bill(record)

# --- MONTH PICKER POPUP (For Viewing Data) ---
def open_month_picker():
    top = tk.Toplevel(root)
    top.title("Select Month")
    top.geometry("300x150")
    top.configure(bg="white")
    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 75
    top.geometry(f"+{x}+{y}")
    lbl = tk.Label(top, text="Select Month & Year", font=FONT_BOLD, bg="white")
    lbl.pack(pady=10)
    frame = tk.Frame(top, bg="white")
    frame.pack(pady=5)
    month_names = list(calendar.month_name)[1:]
    cur_month_index = int(datetime.now().strftime("%m")) - 1
    cur_month_name = month_names[cur_month_index]
    cb_month = ttk.Combobox(frame, values=month_names, width=12, state="readonly", font=FONT_NORMAL)
    cb_month.set(cur_month_name)
    cb_month.pack(side="left", padx=5)
    cur_year = int(datetime.now().strftime("%Y"))
    years = [str(y) for y in range(cur_year - 5, cur_year + 6)]
    cb_year = ttk.Combobox(frame, values=years, width=8, state="readonly", font=FONT_NORMAL)
    cb_year.set(str(cur_year))
    cb_year.pack(side="left", padx=5)
    def apply_filter():
        sel_name = cb_month.get()
        sel_year = cb_year.get()
        if sel_name in month_names:
            m_num = str(month_names.index(sel_name) + 1).zfill(2)
        else: return
        target = f"-{m_num}-{sel_year}" 
        tree.delete(*tree.get_children())
        all_records = fetch_all()
        filtered = []
        if all_records:
            for i, r in enumerate(all_records):
                if target in r[1]: 
                    r_list = list(r)
                    if len(r_list) > 2: del r_list[2] # Remove Time
                    tag = "incomplete" if r[13].lower() == "incomplete" else ("even" if i % 2 == 0 else "odd")
                    tree.insert("", "end", values=r_list, tags=(tag,))
        update_footer(filtered)
        top.destroy()
    btn = tk.Button(top, text="SHOW DATA", bg="#E91E63", fg="white", font=FONT_BOLD, command=apply_filter)
    btn.pack(pady=15, fill="x", padx=20)

# --- IMPORT EXCEL LOGIC ---
def import_excel_data():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if not file_path:
        return False 

    try:
        df = pd.read_excel(file_path)
        df.columns = [str(c).upper().strip() for c in df.columns]
        
        # Confirm Popup
        num_records = len(df)
        file_name = os.path.basename(file_path)
        confirm = messagebox.askyesno("Confirm Import", f"File: {file_name}\n\nFound {num_records} records.\n\nImport them now?")
        
        if not confirm:
            return False

        all_rows = fetch_all()
        current_sno = (max([r[0] for r in all_rows]) + 1) if all_rows else 1
        success_count = 0
        
        for index, row in df.iterrows():
            # --- NEW LOGIC START ---
            raw_cust = str(row.get("CUSTOMER", ""))
            customer = raw_cust.strip() # Remove extra spaces
            
            # If name is empty after stripping, SKIP IT
            if not customer: 
                continue
            # --- NEW LOGIC END ---

            date_val = str(row.get("DATE", datetime.now().strftime("%d-%m-%Y")))
            item = str(row.get("ITEM", ""))
            
            # (Note: we already checked customer above, so we don't need the old 'nan' check here)
            
            count_val = str(row.get("COUNT", "0"))
            qty = to_float(row.get("QUANTITY", 0))
            rate = to_float(row.get("RATE", 0))
            adv = to_float(row.get("ADVANCE", 0))
            phone = str(row.get("PHONE", ""))
            location = str(row.get("LOCATION", ""))
            payment = str(row.get("PAYMENT", "Incomplete"))
            
            total = qty * rate
            amount = total - adv
            if amount < 0: amount = 0.0
            
            time_val = datetime.now().strftime("%H:%M:%S")
            
            values = [current_sno, date_val, time_val, customer, item, count_val, qty, rate, total, adv, amount, phone, location, payment]
            insert_record(values)
            current_sno += 1
            success_count += 1
            
        root.after(0, load_all)
        root.after(0, lambda: messagebox.showinfo("Success", f"Successfully imported {success_count} records!"))
        return True
        
    except Exception as e:
        err_msg = str(e)
        root.after(0, lambda: messagebox.showerror("Import Error", f"Failed to import excel:\n{err_msg}"))
        return False

# ================= DATA ENTRY LOGIC =================
def calculate_live(event):
    try:
        q_val = entries["QUANTITY"].get()
        r_val = entries["RATE"].get()
        a_val = entries["ADVANCE PAID"].get()
        qty = float(q_val) if q_val else 0.0
        rate = float(r_val) if r_val else 0.0
        adv = float(a_val) if a_val else 0.0
        total = qty * rate
        amount = total - adv
        if amount < 0: amount = 0.0
        entries["TOTAL"].delete(0, tk.END)
        entries["TOTAL"].insert(0, f"{total:.2f}")
        entries["AMOUNT"].delete(0, tk.END)
        entries["AMOUNT"].insert(0, f"{amount:.2f}")
    except ValueError: pass

def add_data():
    sno_str = entries["S.NO"].get().strip()
    if not sno_str:
        try:
            all_rows = fetch_all()
            sno = (max([r[0] for r in all_rows]) + 1) if all_rows else 1
        except Exception: return
    else:
        sno = int(sno_str)
        if fetch_by_sno(sno):
            messagebox.showerror("Error", "Duplicate S.NO")
            return
    try:
        date_val = entries["DATE"].get().strip()
        if not date_val: date_val = datetime.now().strftime("%d-%m-%Y")
        time_val = datetime.now().strftime("%H:%M:%S")

        qty = to_float(entries["QUANTITY"].get())
        rate = to_float(entries["RATE"].get())
        adv = to_float(entries["ADVANCE PAID"].get())
        total = qty * rate
        amount = total - adv
        if amount < 0: amount = 0.0
        count_val = entries["COUNT"].get().strip()
        values = [
            sno, date_val, time_val,
            entries["CUSTOMER"].get(), entries["ITEM"].get(),
            count_val, qty, rate,
            total, adv, amount, 
            entries["PHONE"].get(), entries["LOCATION"].get(), entries["PAYMENT"].get()
        ]
        insert_record(values)
        load_all()
        clear_entries()
        entries["S.NO"].config(state="normal")
        messagebox.showinfo("Success", "Record Added")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add: {e}")

def update_data():
    sno = entries["S.NO"].get()
    if not sno.isdigit():
        messagebox.showerror("Error", "Select a record")
        return
    date_val = entries["DATE"].get().strip()
    if not date_val: date_val = datetime.now().strftime("%d-%m-%Y")
    time_val = datetime.now().strftime("%H:%M:%S")

    qty = to_float(entries["QUANTITY"].get())
    rate = to_float(entries["RATE"].get())
    adv = to_float(entries["ADVANCE PAID"].get())
    total = qty * rate
    amount = total - adv
    if amount < 0: amount = 0.0
    count_val = entries["COUNT"].get().strip()

    values = [
        date_val, time_val,
        entries["CUSTOMER"].get(), entries["ITEM"].get(),
        count_val, qty, rate,
        total, adv, amount,
        entries["PHONE"].get(), entries["LOCATION"].get(),
        entries["PAYMENT"].get(), int(sno)
    ]
    try:
        update_record(values)
        load_all()
        clear_entries()
        entries["S.NO"].config(state="normal")
        messagebox.showinfo("Success", "Record Updated")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_data():
    # 1. Check if rows are selected in the table (Highlighted)
    selected_items = tree.selection()
    
    if selected_items:
        # --- MULTIPLE DELETE MODE ---
        count = len(selected_items)
        if not messagebox.askyesno("Confirm Selection", f"Are you sure you want to delete {count} selected records?"):
            return
        
        try:
            for item_id in selected_items:
                values = tree.item(item_id, "values")
                if values:
                    sno = int(values[0]) # Get S.NO from the first column
                    delete_record(sno)   # Delete from database
            
            load_all()     # Refresh table
            clear_entries() # Clear inputs
            entries["S.NO"].config(state="normal")
            messagebox.showinfo("Success", f"Successfully deleted {count} records.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
            
    else:
        # --- SINGLE DELETE MODE (Manual Entry) ---
        sno = entries["S.NO"].get()
        if not sno.isdigit():
            messagebox.showerror("Error", "Please select rows in the table to delete.")
            return
            
        if messagebox.askyesno("Confirm", f"Delete S.NO {sno}?"):
            try:
                delete_record(int(sno))
                load_all()
                clear_entries()
                entries["S.NO"].config(state="normal")
            except Exception as e:
                messagebox.showerror("Error", str(e))

# ================= INPUT FORM FIELDS =================
fields = [
    "S.NO", "DATE", "CUSTOMER", "ITEM", "COUNT", "QUANTITY", "RATE",
    "TOTAL", "ADVANCE PAID", "AMOUNT", "PHONE", "LOCATION", "PAYMENT"
]

entries = {}
suggestion_box = tk.Listbox(root, height=5, font=FONT_NORMAL, bg="#ffffe0")
suggestion_box.place_forget()

# --- AUTO-FILL HELPER FUNCTIONS ---
def get_all_item_names_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        row = cur.fetchone()
        if not row: return []
        tbl = row[0]
        cur.execute(f"SELECT DISTINCT ITEM FROM {tbl} WHERE ITEM IS NOT NULL AND ITEM != ''")
        items = [r[0] for r in cur.fetchall()]
        conn.close()
        return items
    except: return []

# --- MODIFIED: Auto-Fill details now handles Phone AND Location ---
def auto_fill_details(name):
    try:
        records = fetch_by_customer(name)
        if records:
            last_record = records[-1]
            
            # Fill Phone (Index 11)
            phone = last_record[11]
            if phone and not entries["PHONE"].get().strip():
                entries["PHONE"].delete(0, tk.END)
                entries["PHONE"].insert(0, phone)
            
            # Fill Location (Index 12)
            location = last_record[12]
            if location and not entries["LOCATION"].get().strip():
                entries["LOCATION"].delete(0, tk.END)
                entries["LOCATION"].insert(0, location)
    except Exception: pass

def auto_fill_rate(item_name):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        row = cur.fetchone()
        if not row: return
        tbl = row[0]
        cur.execute(f"SELECT RATE FROM {tbl} WHERE ITEM = ? ORDER BY SNO DESC LIMIT 1", (item_name,))
        res = cur.fetchone()
        conn.close()
        if res:
            rate_val = res[0]
            entries["RATE"].delete(0, tk.END)
            entries["RATE"].insert(0, str(rate_val))
            calculate_live(None)
    except: pass

def show_customer_suggestions(event):
    entry = entries["CUSTOMER"]
    typed = entry.get()
    all_names = get_all_customer_names()
    filtered = [n for n in all_names if typed.lower() in n.lower()]
    if not filtered or typed.strip() == "":
        suggestion_box.place_forget()
        return
    suggestion_box.delete(0, tk.END)
    for name in filtered: suggestion_box.insert(tk.END, name)
    x = entry.winfo_rootx() - root.winfo_rootx()
    y = entry.winfo_rooty() - root.winfo_rooty() + entry.winfo_height()
    suggestion_box.place(x=x, y=y, width=entry.winfo_width())
    suggestion_box.lift()
    suggestion_box.bind("<<ListboxSelect>>", fill_customer_suggestion)

def fill_customer_suggestion(event):
    sel = suggestion_box.curselection()
    if sel:
        name = suggestion_box.get(sel[0])
        entries["CUSTOMER"].delete(0, tk.END)
        entries["CUSTOMER"].insert(0, name)
        suggestion_box.place_forget()
        auto_fill_details(name) # Changed call to new function name

def show_item_suggestions(event):
    entry = entries["ITEM"]
    typed = entry.get()
    all_items = get_all_item_names_db()
    filtered = [n for n in all_items if typed.lower() in n.lower()]
    if not filtered or typed.strip() == "":
        suggestion_box.place_forget()
        return
    suggestion_box.delete(0, tk.END)
    for name in filtered: suggestion_box.insert(tk.END, name)
    x = entry.winfo_rootx() - root.winfo_rootx()
    y = entry.winfo_rooty() - root.winfo_rooty() + entry.winfo_height()
    suggestion_box.place(x=x, y=y, width=entry.winfo_width())
    suggestion_box.lift()
    suggestion_box.bind("<<ListboxSelect>>", fill_item_suggestion)

def fill_item_suggestion(event):
    sel = suggestion_box.curselection()
    if sel:
        item = suggestion_box.get(sel[0])
        entries["ITEM"].delete(0, tk.END)
        entries["ITEM"].insert(0, item)
        suggestion_box.place_forget()
        auto_fill_rate(item)

def on_customer_focus_out(event):
    root.after(200, lambda: suggestion_box.place_forget())
    name = entries["CUSTOMER"].get().strip()
    if name: auto_fill_details(name) # Changed call to new function name

def on_item_focus_out(event):
    root.after(200, lambda: suggestion_box.place_forget())
    item = entries["ITEM"].get().strip()
    if item: auto_fill_rate(item)

def show_all_suggestions(field_name):
    if suggestion_box.winfo_ismapped():
        suggestion_box.place_forget()
        return
    
    if field_name == "CUSTOMER":
        entry = entries["CUSTOMER"]
        items = get_all_customer_names()
        func = fill_customer_suggestion
    else:
        entry = entries["ITEM"]
        items = get_all_item_names_db()
        func = fill_item_suggestion

    if not items: return
    suggestion_box.delete(0, tk.END)
    for name in items: suggestion_box.insert(tk.END, name)
    x = entry.winfo_rootx() - root.winfo_rootx()
    y = entry.winfo_rooty() - root.winfo_rooty() + entry.winfo_height()
    suggestion_box.place(x=x, y=y, width=entry.winfo_width())
    suggestion_box.lift()
    suggestion_box.bind("<<ListboxSelect>>", func)
    entry.focus_set()

def auto_sno(event):
    if not entries["S.NO"].get():
        try:
            all_rows = fetch_all()
            next_no = (max([r[0] for r in all_rows]) + 1) if all_rows else 1
            entries["S.NO"].delete(0, tk.END)
            entries["S.NO"].insert(0, str(next_no))
        except Exception: pass

# --- GENERATE FIELDS ---
for i, f in enumerate(fields):
    tk.Label(root, text=f, font=FONT_BOLD).grid(row=i//4, column=(i%4)*2, padx=8, pady=6, sticky="e")
    
    if f == "CUSTOMER":
        c = tk.Frame(root)
        c.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        e = tk.Entry(c, width=23, font=FONT_NORMAL)
        e.pack(side="left", fill="both", expand=True)
        e.bind("<KeyRelease>", show_customer_suggestions)
        e.bind("<FocusOut>", on_customer_focus_out)
        b = tk.Button(c, text="▼", width=2, bg="#ddd", command=lambda: show_all_suggestions("CUSTOMER"))
        b.pack(side="right")
        entries[f] = e

    elif f == "ITEM":
        c = tk.Frame(root)
        c.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        e = tk.Entry(c, width=23, font=FONT_NORMAL)
        e.pack(side="left", fill="both", expand=True)
        e.bind("<KeyRelease>", show_item_suggestions)
        e.bind("<FocusOut>", on_item_focus_out)
        b = tk.Button(c, text="▼", width=2, bg="#ddd", command=lambda: show_all_suggestions("ITEM"))
        b.pack(side="right")
        entries[f] = e

    elif f == "DATE":
        c = tk.Frame(root)
        c.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        e = tk.Entry(c, width=23, font=FONT_NORMAL)
        e.pack(side="left", fill="both", expand=True)
        e.bind("<Button-1>", lambda event, entry=e: show_calendar(event, entry)) 
        e.bind("<FocusIn>", lambda event, entry=e: show_calendar(event, entry)) 
        b = tk.Label(c, text="📅", font=("Segoe UI Emoji", 12), bg="white", fg="#444", cursor="hand2")
        b.pack(side="right", padx=2)
        b.bind("<Button-1>", lambda event, entry=e: show_calendar(event, entry))
        b.bind("<Enter>", lambda event, entry=e: show_calendar(event, entry))
        entries[f] = e

    elif f == "S.NO":
        e = tk.Entry(root, width=26, font=FONT_NORMAL)
        e.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        e.bind("<FocusIn>", auto_sno)
        entries[f] = e
    elif f == "PAYMENT":
        cb = ttk.Combobox(root, values=["Done", "Incomplete"], state="readonly", width=20)
        cb.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        entries[f] = cb
    else:
        e = tk.Entry(root, width=26, font=FONT_NORMAL)
        e.grid(row=i//4, column=(i%4)*2+1, padx=6, pady=6, sticky="w")
        if f in ["QUANTITY", "RATE", "ADVANCE PAID"]:
            e.bind("<KeyRelease>", calculate_live)
        entries[f] = e

# ================= BUTTONS BAR =================
btn_frame = tk.Frame(root)
btn_frame.grid(row=4, column=0, columnspan=11, sticky="ew", pady=15)
for i in range(11): 
    btn_frame.grid_columnconfigure(i, weight=1)

BTN_W = 140
BTN_PAD = 1 

AnimatedButton(btn_frame, "BACK", back_to_normal, "#999999", width=BTN_W).grid(row=0, column=0, padx=BTN_PAD)
AnimatedButton(btn_frame, "UPDATE", update_data, "#ff4444", width=BTN_W).grid(row=0, column=1, padx=BTN_PAD)
AnimatedButton(btn_frame, "DELETE", delete_data, "#D32F2F", width=BTN_W).grid(row=0, column=2, padx=BTN_PAD)
AnimatedButton(btn_frame, "SHOW ALL", load_all, "#FFC107", "black", width=BTN_W).grid(row=0, column=3, padx=BTN_PAD)
AnimatedButton(btn_frame, "SEARCH NAME", lambda: search_logic("name"), "#555555", width=BTN_W).grid(row=0, column=4, padx=BTN_PAD)
AnimatedButton(btn_frame, "VIEW MONTH", open_month_picker, "#E91E63", width=BTN_W).grid(row=0, column=5, padx=BTN_PAD)
AnimatedButton(btn_frame, "FILTER ITEM", filter_by_item, "#9C27B0", width=BTN_W).grid(row=0, column=6, padx=BTN_PAD)
AnimatedButton(btn_frame, "FILTER PAY", filter_by_payment, "#9C27B0", width=BTN_W).grid(row=0, column=7, padx=BTN_PAD)
AnimatedButton(btn_frame, "VIEW BILL", view_bill, "#00BCD4", width=BTN_W).grid(row=0, column=8, padx=BTN_PAD)
AnimatedButton(btn_frame, "ADD", add_data, "#4CAF50", width=BTN_W).grid(row=0, column=9, padx=BTN_PAD)

# --- REPLACED: NEW COMPLEX ANIMATED IMPORT BUTTON ---
DownloadAnimatedButton(btn_frame, "IMPORT EXCEL", import_excel_data, "#2E7D32", width=BTN_W).grid(row=0, column=10, padx=BTN_PAD)

# ================= TABLE & STATUS =================
cols = ["S.NO","DATE","CUSTOMER","ITEM","COUNT","QUANTITY","RATE","TOTAL","ADVANCE PAID","AMOUNT","PHONE","LOCATION","PAYMENT"]
cw = {"S.NO":60, "DATE":115, "CUSTOMER":300, "ITEM":145, "COUNT":110, "QUANTITY":125, "RATE":85, "TOTAL":120, "ADVANCE PAID":170, "AMOUNT":128, "PHONE":130, "LOCATION":150, "PAYMENT":140}

frame = tk.Frame(root)
frame.grid(row=5, column=0, columnspan=11, sticky="nsew")

tree = ttk.Treeview(frame, columns=cols, show="headings", height=20, selectmode="extended")
tree.tag_configure("odd", background="white") 
tree.tag_configure("even", background="#f2f2f2") 
tree.tag_configure("incomplete", background="#ffcccc")
tree.pack(fill="both", expand=True)

def calculate_column_sum(col_name):
    selected_items = tree.selection()
    total = 0.0
    if selected_items:
        target_rows = selected_items
        mode = "SELECTED"
    else:
        target_rows = tree.get_children()
        mode = "ALL VISIBLE"
    for child in target_rows:
        val = tree.set(child, col_name)
        try: total += float(val)
        except (ValueError, TypeError): pass
    messagebox.showinfo(f"Sum ({mode})", f"Sum of {col_name}:  {total:,.2f}")

for c in cols:
    tree.heading(c, text=c, anchor="center", command=lambda _c=c: calculate_column_sum(_c))
    tree.column(c, width=cw[c], anchor="center", stretch=False)

tree.bind("<<TreeviewSelect>>", on_row_select)

status_frame = tk.Frame(root, bg="#333333", height=35)
status_frame.grid(row=6, column=0, columnspan=11, sticky="ew")
status_label = tk.Label(status_frame, text="Ready", bg="#333333", fg="white", font=FONT_FOOTER)
status_label.pack(side="right", padx=20, pady=5)

load_all()
root.mainloop()