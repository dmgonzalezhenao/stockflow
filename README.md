# 📈 StockFlow 
### Smart Inventory Management with Asynchronous Architecture v1.0

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

---

## 🚀 Overview

**StockFlow** is a modern Single Page Application (SPA) style web tool designed to simplify inventory management for small businesses. 

Unlike traditional tools that feel slow or cluttered, StockFlow focuses on a **fluid user experience**. By implementing an asynchronous architecture, the app eliminates unnecessary page refreshes, providing a desktop-like feel directly in the browser.

### 🎥 [Watch the Video Demo](https://youtu.be/BSRfLEa5_W4)

---

## ✨ Key Features

* **⚡ Seamless Interaction:** Uses **AJAX & Fetch API** to handle transactions and stock updates in real-time without reloading the page.
* **⚠️ Low Stock Alert System:** Intelligent monitoring that triggers visual notifications when products fall below a safety threshold.
* **💰 Automated Financials:** Real-time calculation of total inventory value and unit pricing logic.
* **📜 Audit Trail:** A robust **Transaction Log** that records every movement with timestamps, ensuring accountability and data integrity.
* **📱 Fully Responsive:** Crafted with **Bootstrap 5** to ensure a perfect experience on desktops, tablets, and mobile devices.

---

## 🛠️ Technical Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **Frontend** | JavaScript (ES6+), HTML5, CSS3, Bootstrap 5 |
| **Database** | SQLite (Relational Schema) |
| **Architecture** | Asynchronous (Partial DOM injection via AJAX) |

---

## 🧠 Technical Challenges & Decisions

### The Asynchronous Challenge
One of the project's core goals was to master the **DOM manipulation**. I implemented a system where Flask detects AJAX requests and returns only the necessary HTML fragments. This reduces server load and significantly improves the perceived speed for the user.

### Data Integrity
To prevent human error, I designed a relational database where the `products` table and the `transactions` table are synchronized. Every stock change is backed by an immutable record in the audit log, following best practices for financial software.

---

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/tu-usuario/stockflow.git](https://github.com/tu-usuario/stockflow.git)

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt

3. **Run the application**
    ```bash
    flask run

---

## 🗺️ Roadmap & Future Enhancements

The current version of **StockFlow** establishes a solid foundation for inventory management. To further evolve the platform, the following strategic updates are planned:

* **Dynamic Resource Updates:** Implementation of a dedicated module to modify existing product metadata (names, descriptions, and categories) ensuring data remains current without record duplication.
* **Bulk Data Integration:** Development of a CSV/Excel import engine to facilitate the high-volume migration of product catalogs, optimizing the onboarding process for new businesses.
* **Enterprise-Grade Persistence:** Migration from SQLite to **PostgreSQL** to support concurrent connections, enhanced data integrity, and production-ready scalability.
* **Containerization & Deployment:** Dockerizing the application environment to ensure cross-platform consistency and deploying a live instance (via cloud services) to make the tool accessible via web without local environment configuration.

---

## 📝 Final Thoughts

This project was developed as the capstone for **CS50’s Introduction to Computer Science.** It represents a synthesis of SQL database management, Python logic, and advanced JavaScript interaction.

Developed by Daniel Mitchell González Henao - 2024

