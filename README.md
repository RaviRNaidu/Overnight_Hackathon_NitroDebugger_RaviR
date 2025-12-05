# Agricultural Input Subsidy Leakage Detection – Farmer Portal UI

## 📌 Project Overview

This project provides a *clean, modern, government-themed web UI* for a Farmer Subsidy Portal.  
It supports the workflow of an *Agricultural Input Subsidy Leakage Detection System* by digitizing farmer applications and enabling status tracking.  
This repository contains *UI-only pages* for forms, logins, and tracking—no backend or authentication logic.

---

## 🧩 Problem Context (Summary)

India spends over *₹70,000 crores* annually on agricultural input subsidies.  
A large portion is lost due to:

- Fake or ghost beneficiaries  
- Diversion of subsidized goods  
- Manipulated invoices and inflated claims  

A digital portal is the first step to capturing accurate information, reducing leakage, and ensuring genuine farmers receive support.

---

## 🎯 Objectives

- Provide a structured *application form* for farmers.  
- Offer an *application tracking* interface for transparency.  
- Create separate *login UIs* for Agriculture & Horticulture departments.  
- Maintain a *professional, government-like UI theme*.

---

## 🏗 Features

### 1. Navigation Bar
Includes links to:
- Application Form  
- Application Tracker  
- Horticulture Department Login  
- Agriculture Department Login  

---

### 2. Farmer Application Form
Form fields include:
- Farmer Name  
- Aadhaar Number  
- Mobile Number  
- Address  
- Total Land Acres  
- Crop Type  
- Fertilizer Requirement  
- Department Selector (Agriculture / Horticulture)

---

### 3. Application Tracker
Inputs:
- Application ID  
- Mobile Number  

Displays (placeholder UI):
- Status: Approved / Pending / Rejected  
- Department Handling the Request  

---

### 4. Department Logins
Separate login pages for:
- *Agriculture Department*
- *Horticulture Department*

Each login includes:
- User ID  
- Password
- Login Button  

> Note: Only UI; no backend validation implemented.

---

## 🎨 UI Style & Theme

The portal follows a *clean government portal theme*:

- *Colors:* Blue + White  
- *Rounded form fields*  
- *Simple icons*  
- *Responsive layout*  
- *Minimal, modern front-end structure*  

---

## 📁 Project Structure

project-root/
├─ index.html # Home page with navbar
├─ application-form.html # Farmer Application Form
├─ application-tracker.html # Application Tracker
├─ agri-login.html # Agriculture Department Login
├─ horti-login.html # Horticulture Department Login
├─ css/
│ └─ styles.css # Custom CSS for govt-theme
└─ js/
└─ main.js # Optional interactivity
