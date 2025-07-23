#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import re
from old_diagnoses import old_diagnoses
from setuptools.command.build_ext import link_shared_object

id_number = set(())

def check_dictionary_key(doc, key):
    """
    Check if key exists and is not empty in dictionary
    Returns: True if key exists and has value, False otherwise
    """
    if key not in doc:  # Key doesn't exist
        return False
    if doc[key] is None:  # Key exists but is None
        return False
    if isinstance(doc[key], str) and not doc[key].strip():  # Empty string or only whitespace
        return False
    if isinstance(doc[key], (list, dict)) and not doc[key]:  # Empty list or dict
        return False
    return True


def main():
    global document_count , len_patients
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)  # 5-second timeout
        # Test the connection
        client.server_info()

        db = client['emcell']  # Connect to emcell database
        patients_collection = db['patients']  # Get the patients collection
        # Check if a collection is empty
        document_count = patients_collection.count_documents({})
        if document_count == 0:
            print("The patients collection is empty")
        else:
            print(f"Found {document_count} documents in the collection")

        try:
            # Read all documents from the patients collection
            patients = patients_collection.find()
            len_patients = len(patients)
            counter = 0
            # Print each patient document
            for i, patient in enumerate(patients):
                counter += 1
                if check_dictionary_key(patient, 'number'):
                    code_numbers = patient['number'].split('-')
                    number_counter = '{}'.format(code_numbers[1][1:] if code_numbers[1].startswith('0') else code_numbers[1])
                    if len(code_numbers[0]) >6:
                        # Remove the 4th and 5th symbols (index 3 and 4 in zero-based indexing)
                        number_normalize = code_numbers[0][:4] + code_numbers[0][6:]
                        code_numbers[0] = number_normalize
                    # make the correct number
                    code_of_number = code_numbers[0] + '-' + str(number_counter)
                    if code_of_number in id_number:
                        print(f"Duplicate code found: {code_of_number}")
                    else:
                        id_number.add(code_of_number)

                    # print(f"{counter:5d}:{code_numbers} i:{i:5} => {code_of_number}")


        except OperationFailure as e:
            print(f"An error occurred while querying the database: {e}")

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"len_patients = {len_patients} ")
        print(f"Found {document_count} documents in the collection")
    finally:
        # Close the connection in the finally block to ensure it always happens
        try:
            client.close()
            print("MongoDB connection closed")
        except NameError:
            # In case the client was never created
            pass

if __name__ == "__main__":
    main()
