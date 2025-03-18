import json
import os
import pymysql
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

DB_HOST = config["DB_HOST"]
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
DB_NAME = config["DB_NAME"]

# Establish a database connection
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to handle invalid timestamps
def fix_datetime(value):
    if value == "1970-01-01 00:00:00":
        return None  # Convert invalid timestamp to NULL
    return value

@app.route("/join_visit_phone", methods=["POST"])
def join_visit_phone():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request, no data provided"}), 400
        
        user_id = data.get("UserID")
        ip_id = data.get("IPID")
        ad_id = data.get("AdID")
        view_date = fix_datetime(data.get("ViewDate"))
        phone_request_date = fix_datetime(data.get("PhoneRequestDate"))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO VisitPhoneRequestStream 
                (UserID, IPID, AdID, ViewDate, PhoneRequestDate, inserted_at) 
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(sql, (user_id, ip_id, ad_id, view_date, phone_request_date))
            conn.commit()

        conn.close()
        return jsonify({"message": "Data successfully inserted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
