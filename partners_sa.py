#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import re
from old_diagnoses import old_diagnoses
from setuptools.command.build_ext import link_shared_object

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

def semantic_analysis(partner):
    record= {'id': str(partner['_id'])}


    # fill in the 'lastName' and 'firstname' fields
    if check_dictionary_key(partner, 'lastName'):
        record['lastName'] = partner['lastName'].capitalize()
        if check_dictionary_key(partner, 'firstName'):
            record['firstName'] = partner['firstName'].capitalize()
        else:
            record['firstName'] = ''
    else:
        if check_dictionary_key(partner, 'fullName'):
            res_last = re.findall(r'\b\w+\b', partner['fullName'])[-1]
            record['lastName'] = res_last.capitalize().strip()
            res_first = partner['fullName'].replace(res_last, '').strip()
            record['firstName'] = res_first.capitalize().strip() if res_first else ''
        else:
            record['lastName'] = ''
            if check_dictionary_key(partner, 'firstName'):
                record['firstName'] = partner['firstName'].capitalize()
            else:
                record['firstName'] = ''

# gender
    if check_dictionary_key(partner, 'gender'):
        record['gender'] = partner['gender']
    else:
        record['gender'] = ''

# age
    if check_dictionary_key(partner, 'age'):
        record['age'] = partner['age']
    else:
        record['age'] = ''

# DOB
    if check_dictionary_key(partner, 'birthDate'):
        record['birthDate'] = partner['birthDate'].strftime("%Y-%m-%d")

# companies
    if check_dictionary_key(partner, '_companies'):
        record['company'] = str(partner['_companies'])
    else:
        record['company'] = ''

#  Emails
    if check_dictionary_key(partner, '_mails'):
        emails = partner['_mails'].split(',')
        # Normalize emails by removing spaces
        emails = [email.strip() for email in emails if email.strip()]
        record['email'] = emails[0] if emails else ''
        skip0=True
        if len(emails) > 1:
            for email in emails:
                # If there are multiple emails, take the next ones as alternative emails
                if skip0:
                    skip0=False
                    continue
                record['alt_emails'] = str(email).strip()+";"
        else: # If no emails are found, set to empty strings
            record['alt_emails'] = ''
    else:
        record['email'] = ''
        record['alt_emails'] = ''

    #  Phone numbers
    if check_dictionary_key(partner, '_phones'):
        phones = partner['_phones'].split(',')
        # Normalize phone numbers by removing spaces and dashes
        # phones = [phone.strip().replace(' ', '').replace('-', '') for phone in phones if phone.strip()]
        record['phone'] = phones[0].strip()
        skip0=True
        if len(phones) > 1:
            for phone in phones:
                # If there are multiple phone numbers, take the next ones as alternative phones
                if skip0:
                    skip0=False
                    continue
                record['alt_phones'] = str(phone).strip()+";"
        else: # If no phone numbers are found, set to empty strings
            record['alt_phones'] = ''
    else:
        record['phone'] = ''
        record['alt_phones'] = ''




    return record







def main():
    global partners_db
    try:
        # Connect to MongoDB
        partners_db = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)  # 5-second timeout
        # Test the connection
        partners_db.server_info()

        db = partners_db['emcell']  # Connect to emcell database
        partners_collection = db['partners']  # Get the partners collection
        # Check if a collection is empty
        document_count = partners_collection.count_documents({})
        if document_count == 0:
            print("The partners collection is empty")
        else:
            print(f"Found {document_count} documents in the collection")

        try:
            # Read all documents from the partners collection
            partners = partners_collection.find()

            counter = 0
            # Print each partner document
            for partner in partners:
                record=semantic_analysis(partner)
                print(record)
                counter += 1
                if counter >25:
                    break
                # if counter % 1000 == 0:
                #     print(f"Processed {counter} partner records.")
            # print(f"Processed {counter} partner records.")

        except OperationFailure as e:
            print(f"An error occurred while querying the database: {e}")

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection in the finally block to ensure it always happens
        try:
            partners_db.close()
            print("MongoDB connection closed")
        except NameError:
            # In case the client was never created
            pass

if __name__ == "__main__":
    main()
