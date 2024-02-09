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
GET_CUSTOMERS_DATA = "SELECT * FROM customers LIMIT 1000;"
GET_CUSTOMER_BY_ID = "SELECT * FROM customers WHERE id = %s;"
INSERT_CUSTOMER_RETURN_DATA = "INSERT INTO customers (name, ig_account, fav_color) VALUES (%s, %s, %s) RETURNING id, name, ig_account, fav_color;"
UPDATE_CUSTOMER_RETURN_DATA = "UPDATE customers SET name=%s, ig_account=%s, fav_color=%s WHERE id=%s RETURNING id, name, ig_account, fav_color;"
DELETE_CUSTOMER_RETURN_ID = "DELETE FROM customers WHERE id=%s RETURNING id;"

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
                cursor.execute(INSERT_CUSTOMER_RETURN_DATA, (name, ig_account,fav_color))
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
    return {"data": data, "message": f"{name} has been created as new customer.", "status_code": 200}
            
# update
@app.put("/api/update/customer/<id>")
def update_customer(id):
    try:
        data = request.get_json()
        name = data['name']
        ig_account = data['ig_account']
        fav_color = data['fav_color']
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_CUSTOMER_RETURN_DATA, (name, ig_account,fav_color, id))
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
    return {"data": data, "message": f"{name} data has been updated.", "status_code": 200}

# delete
@app.delete("/api/delete/customer/<id>")
def delete_customer(id):
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_CUSTOMER_RETURN_ID, (id,))
                customer_id = ''
                customer_id = cursor.fetchone()[0]
                if not customer_id:
                    raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"id": customer_id, "message": "Customer has been deleted.", "status_code": 200}