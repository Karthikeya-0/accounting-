import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk, ImageGrab

def show_bill(record):
    # --- 1. Create Window ---
    bill_win = tk.Toplevel()
    bill_win.title("Invoice View")
    bill_win.geometry("576x900")
    bill_win.resizable(True, True)

    # --- 2. Create Canvas ---
    c = tk.Canvas(bill_win, bg="white")
    c.pack(fill="both", expand=True)

    # --- 3. Load Image Logic ---
    current_folder = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_folder, "bgimg.jpg") 
    
    original_image = None
    if os.path.exists(img_path):
        try:
            original_image = Image.open(img_path)
        except Exception as e:
            print(f"Error opening image: {e}")

    # --- 4. The Draw Function ---
    def draw_content(event=None):
        w = c.winfo_width()
        h = c.winfo_height()
        
        if w < 10 or h < 10: return

        c.delete("all")

        # A. Draw Background
        if original_image:
            try:
                resized_image = original_image.resize((w, h), Image.Resampling.LANCZOS)
                bg_photo = ImageTk.PhotoImage(resized_image)
                c.image_ref = bg_photo
                c.create_image(0, 0, image=bg_photo, anchor="nw")
            except:
                pass
        
        # B. Draw Header & Data
        center_x = w / 2
        left_margin = 50 
        
        # Fonts
        F_HEADER = ("Arial", 24, "bold")
        F_SUB = ("Arial", 14, "bold")
        F_NORMAL = ("Arial", 12)

        # Header Text
        c.create_text(center_x, 60, text="INVOICE / RECEIPT", font=F_HEADER, fill="black")

        # Unpack Record
        r_date, r_time = record[1], record[2]
        r_customer = record[3]
        r_item = record[4]
        r_count = record[5]
        r_qty = record[6]
        r_rate = record[7]
        r_total = record[8]
        r_advance = record[9]
        r_balance = record[10]
        r_phone = record[11]
        r_location = record[12]

        # Draw Text Fields
        start_y = 130
        gap = 30
        
        c.create_text(left_margin, start_y, text=f"Date: {r_date}   Time: {r_time}", font=F_NORMAL, anchor="w", fill="black")
        c.create_text(left_margin, start_y + gap, text=f"Customer: {r_customer}", font=F_SUB, anchor="w", fill="black")
        c.create_text(left_margin, start_y + gap*2, text=f"Phone: {r_phone}", font=F_NORMAL, anchor="w", fill="black")
        c.create_text(left_margin, start_y + gap*3, text=f"Location: {r_location}", font=F_NORMAL, anchor="w", fill="black")
        
        c.create_line(left_margin, start_y + gap*4.5, w - left_margin, start_y + gap*4.5, width=2, fill="black")

        item_y = start_y + gap*6
        c.create_text(left_margin, item_y, text=f"Item: {r_item}", font=F_SUB, anchor="w", fill="black")
        c.create_text(left_margin, item_y + gap, text=f"Count: {r_count}", font=F_NORMAL, anchor="w", fill="black")
        c.create_text(center_x + 50, item_y + gap, text=f"Quantity: {r_qty} kg", font=F_NORMAL, anchor="w", fill="black")
        c.create_text(left_margin, item_y + gap*2, text=f"Rate: {r_rate}", font=F_NORMAL, anchor="w", fill="black")

        c.create_line(left_margin, item_y + gap*3.5, w - left_margin, item_y + gap*3.5, width=2, fill="black")

        money_y = item_y + gap*5
        money_x = center_x + 100 

        c.create_text(money_x, money_y, text=f"Total Bill:   {r_total}", font=F_SUB, anchor="e", fill="black")
        c.create_text(money_x, money_y + gap, text=f"Advance:   -{r_advance}", font=F_NORMAL, anchor="e", fill="red")
        c.create_text(money_x, money_y + gap*2, text=f"Balance:    {r_balance}", font=("Arial", 18, "bold"), anchor="e", fill="green")

        # Footer Message
        c.create_text(left_margin, h - 140, text="CEO & FOUNDER: Lanke venkateswarlu", font=("Arial", 8, "italic"), fill="#333333", anchor="w")

        # --- C. PDF Generation Function ---
        def generate_pdf():
            try:
                # 1. Hide buttons for the screenshot
                btn_print.place_forget()
                btn_close.place_forget()
                bill_win.update() # Force update to remove buttons visually

                # 2. Capture Screenshot
                x = bill_win.winfo_rootx()
                y = bill_win.winfo_rooty()
                w = bill_win.winfo_width()
                h = bill_win.winfo_height()
                
                img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                
                # 3. Convert to RGB (Required for PDF)
                img_rgb = img.convert('RGB')
                
                # 4. Save as PDF
                # This saves "Invoice.pdf" in the same folder as your code
                pdf_path = os.path.join(current_folder, "Invoice.pdf")
                img_rgb.save(pdf_path)
                
                # 5. Restore buttons (Refresh the view)
                draw_content()

                # 6. Open the PDF
                messagebox.showinfo("PDF Saved", f"PDF saved successfully!\nOpening: {pdf_path}")
                os.startfile(pdf_path)

            except Exception as e:
                # Make sure buttons come back even if there is an error
                draw_content()
                messagebox.showerror("Error", f"Failed to make PDF: {e}")

        # --- D. Amazon Style Buttons ---
        btn_font = ("Arial", 11, "bold")
        amazon_yellow = "#F7CA00" 
        text_color    = "#0F1111"

        btn_print = tk.Button(c, text="Print invoice", bg=amazon_yellow, fg=text_color, font=btn_font, relief="raised", cursor="hand2", command=generate_pdf)
        btn_close = tk.Button(c, text="Close", bg="white", fg=text_color, font=btn_font, relief="solid", cursor="hand2", command=bill_win.destroy)

        # Place Buttons
        button_y = h - 60
        btn_width = 140
        gap_btn = 20

        c.create_window(center_x - (btn_width/2) - (gap_btn/2), button_y, window=btn_print, width=btn_width, height=40)
        c.create_window(center_x + (btn_width/2) + (gap_btn/2), button_y, window=btn_close, width=btn_width, height=40)

    # --- 5. Initial Draw & Bind ---
    bill_win.after(100, draw_content)
    c.bind("<Configure>", draw_content)