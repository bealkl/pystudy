#!/usr/bin/env python3
from pymongo import MongoClient
from id_file_func import save_id_numbers, load_id_numbers
from pymongo.errors import OperationFailure
import re

id_number = set()
BATCH_SIZE = 4000  # Process records in batches of 1000

def check_dictionary_key(doc, key):
    if key not in doc:
        return False
    if doc[key] is None:
        return False
    if isinstance(doc[key], str) and not doc[key].strip():
        return False
    if isinstance(doc[key], (list, dict)) and not doc[key]:
        return False
    return True

def normalize_patient_number(number):
    code_numbers = [item.strip() for item in number.split('-')]

    if len(code_numbers) != 2:
        return None

    if len(code_numbers[1]) <=0:
        code_numbers[1]='888'
        # print(f"{code_numbers}       {number}")

    # number_counter = code_numbers[1][1:] if code_numbers[1].startswith('0') else code_numbers[1]
    # Remove 'a' if the second part ends with it
    number_counter = code_numbers[1][:-1] + '99' if code_numbers[1].endswith('a') else code_numbers[1]
    if number_counter.isdigit():
        number_counter = str(int(number_counter))

    if len(code_numbers[0]) > 6:
        number_normalize = code_numbers[0][:4] + code_numbers[0][6:]
        code_numbers[0] = number_normalize

    # print(f"{code_numbers[0]}-{number_counter}")

    return f"{code_numbers[0]}-{number_counter}"

def process_patients_batch(batch):
    for patient in batch:
        # print(f"number: {patient.get('number', 'N/A')}, name: {patient.get('name', 'N/A')}")
        if check_dictionary_key(patient, 'number'):
            # print(f"number: {patient.get('number', 'N/A')}")
            code_of_number = normalize_patient_number(patient['number'])
            if code_of_number:
                if code_of_number in id_number:
                    print(f"Duplicate code found: {code_of_number}. patient: {patient}")
                else:
                    id_number.add(code_of_number)

def main():
    global client
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()

        db = client['emcell']
        patients_collection = db['patients']

        total_documents = patients_collection.count_documents({})
        if total_documents == 0:
            print("The patients collection is empty")
            return

        print(f"Found {total_documents} documents in the collection")

        for skip in range(0, total_documents, BATCH_SIZE):
            batch = patients_collection.find().skip(skip).limit(BATCH_SIZE)
            process_patients_batch(batch)
            print(f"Processed {min(skip + BATCH_SIZE, total_documents)}/{total_documents} records")

# In the main function, add these lines before the try-finally block:
#         id_number = load_id_numbers()

# And at the end of the main function, before the finally block:
        save_id_numbers(id_number)

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
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