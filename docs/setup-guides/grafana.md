# Grafana Setup Guide

Documentation for setting up Grafana.
POC: CSV → MongoDB → Django API → Grafana (SimpleJson Plugin)

This Proof of Concept demonstrates how CSV data can be stored in MongoDB, exposed through a Django REST API, and visualized in Grafana using the SimpleJson data source plugin.

📌 Architecture Overview
CSV File → MongoDB → Django API (REST) → Grafana (SimpleJson)

📁 1. MongoDB Setup
Database & Collection

Database: finance_db

Collection: stock_prices

Steps

Install MongoDB Compass

Click Create Database

Enter:

Database: finance_db

Collection: stock_prices

Import CSV data into the collection

🛠 2. Django API Setup
Dependencies

Install required packages:

pip install pymongo djangorestframework django-cors-headers

MongoDB Connection (settings.py)
MONGO_DB = {
    "host": "localhost",
    "port": 27017,
    "db": "finance_db",
    "collection": "stock_prices"
}

API View (views.py)
from pymongo import MongoClient
from django.http import JsonResponse
from django.conf import settings

def prices(request):
    client = MongoClient(settings.MONGO_DB["host"], settings.MONGO_DB["port"])
    db = client[settings.MONGO_DB["db"]]
    data = list(db[settings.MONGO_DB["collection"]].find({}, {"_id": 0}))
    return JsonResponse(data, safe=False)

API URL (urls.py)
from django.urls import path
from .views import prices

urlpatterns = [
    path('prices/', prices),
]

API Endpoint
http://localhost:8000/prices/

📊 3. Grafana Setup (Windows)
Installation

Installed Grafana OSS
(Enterprise version not used because MongoDB plugin requires license)

Plugin Used

✔ SimpleJson Plugin
This plugin lets Grafana connect to custom APIs like Django.

Configure Data Source

Go to Configuration → Data Sources

Click Add Data Source

Select SimpleJson

Set URL:

http://localhost:8000/prices/


Save & Test → should return success

📈 4. Dashboard Visualization

Create a new dashboard

Add a panel

Select SimpleJson as data source

Data loads from the Django API (which reads from MongoDB)

✔ Result

This POC successfully demonstrates:

MongoDB storing CSV data

Django exposing MongoDB data via REST API

Grafana visualizing data using SimpleJson plugin

Full end-to-end working pipeline
