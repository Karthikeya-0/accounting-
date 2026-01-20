# 🦐 Smart Prawn Accounting System  
### *High-Performance Desktop Accounting Application*

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-0D1117?style=for-the-badge&logo=python&logoColor=FFD43B"/>
  <img src="https://img.shields.io/badge/GUI-Tkinter-0D1117?style=for-the-badge&logo=windows&logoColor=00E5FF"/>
  <img src="https://img.shields.io/badge/Database-SQLite-0D1117?style=for-the-badge&logo=sqlite&logoColor=4DB6AC"/>
  <img src="https://img.shields.io/badge/Excel-Pandas%20%7C%20OpenPyXL-0D1117?style=for-the-badge&logo=microsoft-excel&logoColor=00C853"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0D1117?style=for-the-badge&logo=windows&logoColor=1E90FF"/>
</p>

---

## 📌 Overview

The **Smart Prawn Accounting System** is a professional offline desktop application built using **Python, Tkinter, and SQLite**.

It provides:

- ⚡ High-speed data handling  
- 📥 Excel bulk import  
- 🧾 Automatic bill calculation  
- 📊 Monthly & customer-wise reports  
- 🖥 High-DPI UI support for modern displays  
- 🔐 Secure offline database with auto backup  

Designed for **prawn & fish traders**, this system replaces manual ledgers with a fast, reliable, and clean digital solution.

---

## 🏗️ System Architecture
---
                ┌──────────────────────────┐
                │      Tkinter GUI         │
                │  (Desktop Application)   │
                └───────────┬─────────────┘
                            │  User Input / UI Events
                            ▼
                ┌──────────────────────────┐
                │     Python Core Logic    │
                │ (Validation, Calc, Flow) │
                └───────────┬─────────────┘
                            │  SQL Queries
                            ▼
                ┌──────────────────────────┐
                │     SQLite Database      │
                │  (Offline Local Storage) │
                └───────────┬─────────────┘
                            │
                            ▼
                ┌──────────────────────────┐
                │    Excel Import Engine   │
                │ (Pandas + OpenPyXL)      │
                └──────────────────────────┘


---

## 🚀 Key Features

### 🧾 Accounting & Billing
- Automatic S.NO generation
- Live total & balance calculation
- Bill view and print support

### 📊 Search & Filters
- Search by Customer Name or S.NO
- Filter by Item
- Filter by Payment Status
- Monthly Report Viewer

### 📥 Excel Bulk Import
- Import thousands of records
- Smart validation
- Animated progress indicator

### 🧠 Smart Automation
- Auto-fill customer phone
- Auto-fill item rate
- Name & item suggestions

### 🔐 Data Safety
- Automatic database backup
- Indexed fast queries
- Corruption-safe SQLite

### 🖥 UI & Performance
- AMOLED dark friendly layout
- High DPI scaling (4K Ready)
- Smooth animations
- Custom calendar picker

---

## ⚙️ Technology Stack

| Layer | Technology |
|------|------------|
| GUI | Tkinter |
| Core | Python 3 |
| Database | SQLite |
| Excel | Pandas, OpenPyXL |
| Reports | PDF Generator |
| UI Scaling | Windows Per-Monitor DPI |

---

## 📂 Project Structure

accounting-
│
├── main.py # Main Application
├── operations.py # Database Logic
├── bill_view.py # Bill Generator
├── prawn_accounts.db # SQLite Database
├── Backups/ # Auto Backups
└── README.md

---

## 📊 Excel Column Format
DATE | CUSTOMER | ITEM | COUNT | QUANTITY | RATE | ADVANCE | PHONE | LOCATION | PAYMENT

## 🎓 Academic Use

Perfect for:

Final Year Project

Python GUI Development

Offline Business Automation

Database Application Design

## 👨‍💻 Author

KARTHIKEYA UNDAVALLI
🎓 Computer Science Engineer
🔗 GitHub: https://github.com/Karthikeya-0

📌 Project: Smart Prawn Accounting System



