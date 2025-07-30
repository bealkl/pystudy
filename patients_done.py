#!/usr/bin/env python3
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import pandas as pd
from look4patient import look4patient
import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Initial connection without database
        mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '2Xw7wpkUy7I3',
            'collation': 'utf8mb4_general_ci'
        }

        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS crma")
        cursor.execute("USE crma")

        # Create patients table with all fields from record_pat
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS patients (
                id VARCHAR(255) PRIMARY KEY,
                lastNameOrigin VARCHAR(255),
                lastName VARCHAR(255),
                firstNameOrigin VARCHAR(255),
                firstName VARCHAR(255),
                age VARCHAR(50),
                birthDate DATE,
                gender TINYINT DEFAULT 0,
                language VARCHAR(50),
                number VARCHAR(50),
                status VARCHAR(100),
                passports TEXT,
                country VARCHAR(100),
                partner TEXT,
                phone VARCHAR(255),
                alt_phones TEXT,
                email VARCHAR(255),
                alt_emails TEXT,
                diagnosis TEXT,
                extraDiagnosis TEXT,
                contacts TEXT,
                courses TEXT,
                cureplans TEXT,
                remark TEXT,
                registered DATE,
                wheelchair VARCHAR(50),
                sourceLetter TEXT,
                sourceLetterEnglish TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
                       """)

        conn.commit()
        return conn, cursor

    except Error as e:
        print(f"Error setting up database: {e}")
        return None, None

def write_to_mariadb(record_pat, cursor, conn):
    try:
        # Prepare INSERT statement
        columns = ', '.join(record_pat.keys())
        placeholders = ', '.join(['%s'] * len(record_pat))
        query = f"INSERT INTO patients ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE "
        update_clause = ', '.join([f"{col}=VALUES({col})" for col in record_pat.keys()])
        query += update_clause

        # Convert empty strings to None for DATE fields
        values = list(record_pat.values())
        for i, value in enumerate(values):
            if value == '' and (
                    'birthDate' in record_pat.keys() and list(record_pat.keys())[i] == 'birthDate' or
                    'registered' in record_pat.keys() and list(record_pat.keys())[i] == 'registered'
            ):
                values[i] = None

        # Execute INSERT
        cursor.execute(query, values)
        conn.commit()

    except Error as e:
        print(f"Error inserting record: {e}")
        conn.rollback()

# Modify the existing write_patient_records_to_excel function
def write_patient_records_to_excel(batch_size=100):
    global conn, cursor, client
    try:
        # Setup MariaDB connection
        conn, cursor = setup_database()
        if not conn or not cursor:
            return

        # Connect to MongoDB (your existing code)
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['emcell']
        patients_collection = db['patients']

        total_documents = patients_collection.count_documents({})
        print(f"Total documents to process: {total_documents}")
        processed = 0

        # Process each patient record
        patients_db = patients_collection.find()
        for patient in patients_db:
            record_pat = look4patient(patient)
            # record_pat = processed  # Placeholder for the actual patient record processing
            # if processed % 100 == 0:
            #     print(f"    {len(record_pat)}")
            write_to_mariadb(record_pat, cursor, conn)
            processed += 1
            # record_pat.clear()
            if processed % 1000 == 0:
                print(f"Processed {processed} records")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MariaDB connection closed")
        if 'client' in locals():
            client.close()
            print("MongoDB connection closed")

if __name__ == "__main__":
    write_patient_records_to_excel()
    # print("Patient records written to MariaDB successfully.")