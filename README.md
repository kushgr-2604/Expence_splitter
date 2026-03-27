# Expence_splitter
AI Smart Expense Splitter

A lightweight web application that helps groups easily track and split shared expenses.  
The app uses **OCR (Optical Character Recognition)** to automatically extract payment details from screenshots and split the expense among group members.

Built using **Python, Streamlit, OpenCV, and Tesseract OCR**.

---

# 🚀 Features

### 👥 Group Management
- Create a group
- Add multiple members
- Prevent duplicate members

### 📸 Screenshot-Based Expense Entry
- Upload payment screenshots from apps like **Paytm, GPay, PhonePe**
- Automatically extract text using **Tesseract OCR**

### 💰 Automatic Amount Detection
- Detects amounts like:
  - ₹2,440
  - 2,440
  - 2000
- Filters out UPI IDs and other numbers

### ⚖️ Expense Splitting
- Equal split among group members
- Automatically calculates who owes whom
