import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request
from fastapi import HTTPException

load_dotenv()

app = Flask(__name__)

url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

# Model
# === CUSTOMERS ===
CREATE_CUSTOMERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS customers (id SERIAL PRIMARY KEY, name TEXT, ig_account TEXT, fav_color TEXT);"
)
GET_CUSTOMERS_DATA = "SELECT * FROM customers LIMIT 100;"
GET_CUSTOMER_BY_ID = "SELECT * FROM customers WHERE id = %s;"
INSERT_CUSTOMER_RETURN_ID = "INSERT INTO customers (name, ig_account, fav_color) VALUES (%s, %s, %s) RETURNING id, name, ig_account, fav_color;"

# routes
# === CUSTOMERS ===
# get all
@app.get("/api/customers")
def get_customers():
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_CUSTOMERS_DATA)
                columns = cursor.description
                data = []
                for value in cursor.fetchall():
                    temp = {}
                    for (index, col) in enumerate(value):
                        temp[columns[index][0]] = col
                    data.append(temp)
                if len(data) == 0:
                    raise HTTPException(status_code=404, detail="Customers not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"data": data, "status_code": 200}

# get by id
@app.get("/api/customer/<id>")
def get_customer(id):
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_CUSTOMER_BY_ID, (id,))
                columns = cursor.description
                data = {}
                for value in cursor.fetchall():
                    temp = {}
                    for (index, col) in enumerate(value):
                        temp[columns[index][0]] = col
                    data = temp
                if not data:
                    raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"data": data, "status_code": 200}

# create
@app.post("/api/create/customer")
def create_customer():
    try:
        data = request.get_json()
        name = data['name']
        ig_account = data['ig_account']
        fav_color = data['fav_color']
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_CUSTOMERS_TABLE)
                cursor.execute(INSERT_CUSTOMER_RETURN_ID, (name, ig_account,fav_color))
                columns = cursor.description
                data = {}
                for value in cursor.fetchall():
                    temp = {}
                    for (index, col) in enumerate(value):
                        temp[columns[index][0]] = col
                    data = temp
                if not data:
                    raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"data": data, "message": f"{name} has been created as new customer.", "status_code": 201}
            



