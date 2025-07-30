#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import re
from old_diagnoses import old_diagnoses
from dictionary_utils import check_dictionary_key
from look4patient import look4patient

import pandas as pd
from datetime import datetime

def main():
    global client
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client['emcell']
        patients_collection = db['patients']

        document_count = patients_collection.count_documents({})
        if document_count == 0:
            print("The patients collection is empty")
            return
        print(f"Found {document_count} documents in the collection")

        # Initialize variables
        batch_size = 4000
        excel_file = f"patients_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        batch_records = []
        counter = 0
        batch_number = 1

        try:
            patients = patients_collection.find()
            for patient in patients:
                patient_record = look4patient(patient)
                batch_records.append(patient_record)
                counter += 1

                # Write batch when it reaches batch_size
                if len(batch_records) >= batch_size:
                    # Create new file for each batch
                    excel_file = f"patients_data_batch{batch_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    df = pd.DataFrame(batch_records)
                    df.to_excel(excel_file, index=False)

                    print(f"Wrote batch {batch_number} with {len(batch_records)} records to {excel_file}. Total: {counter}")
                    batch_records = []
                    batch_number += 1

            # Write remaining records
            if batch_records:
                excel_file = f"patients_data_batch{batch_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df = pd.DataFrame(batch_records)
                df.to_excel(excel_file, index=False)
                print(f"Wrote final batch {batch_number} with {len(batch_records)} records to {excel_file}. Total: {counter}")

            print(f"Wrote batch of {len(batch_records)} records. Total: {counter}")


        except PermissionError:
            print(f"Permission denied: Cannot write to {excel_file}")
        except Exception as e:
            print(f"Error writing to Excel: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        try:
            client.close()
            print("MongoDB connection closed")
        except NameError:
            pass

if __name__ == "__main__":
    main()
