# 🚚 Sports Logistics Web App

**Sports Logistics** is a full-featured, role-based logistics management system built with Django. Designed for teams managing sports equipment shipments, orders, events, and warehouse operations, it supports Admins, Warehouse Managers, and Customers with tailored dashboards, real-time analytics, REST APIs, and advanced UI.

---

## 🔍 Features

- 🧑‍💼 **Role-Based Dashboards**:  
  - Admin: Analytics, order/event management  
  - Manager: Shipment and warehouse control  
  - Customer: Track orders & deliveries  

- 🚚 **Shipment & Order Management**  
  - CRUD operations, status tracking, and shipment filters  
  - CSV bulk upload support *(coming soon)*

- 📅 **Event Scheduling**  
  - Create and manage upcoming logistics events  
  - Admin-only access with date/location details

- 🌍 **REST API Integration**  
  - View and manipulate data via `/api/shipments`, `/api/orders`, etc.

- 🔐 **Secure Auth & Permissions**  
  - Django Auth + Profile roles  
  - Login/logout, password validation, role-based access

- 🧪 **Automated Testing**  
  - Unit tests (form validation, permissions)  
  - Selenium: full user journey test with browser automation

- 🎨 **Modern UI/UX**  
  - Responsive Bootstrap 5 interface  
  - Dark navbar, card-based layout, data visualisation with Chart.js

---
## 🛠 Setup Instructions

### 1. Clone the Project

```bash
git clone https://github.com/ianmugo1/sports_logistics.git
cd sports_logistics
