#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import re
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

def look_for(patient):
    record= {'id': str(patient['_id'])}

# fill in the 'lastNameOrigin' field
    if check_dictionary_key(patient, 'lastName'):
        record['lastNameOrigin'] = patient['lastName']
    else:
        record['lastNameOrigin'] = ''

    # fill in the 'lastName' field
    if check_dictionary_key(patient, 'lastNameEnglish'):
        record['lastName'] = patient['lastNameEnglish'].capitalize()
    else:
        if check_dictionary_key(patient, 'fullNameEnglish'):
            # If 'lastNameEnglish' doesn't exist, check 'fullNameEnglish'
            # and assign it to 'lastName' in the record
            record['lastName'] = patient['fullNameEnglish'].capitalize()
        else:
            if check_dictionary_key(patient, 'fullName'):
                # If neither 'lastNameEnglish' nor 'fullNameEnglish' exists,
                # check 'fullName' and assign it to 'lastName' in the record
                record['lastName'] = patient['fullName'].capitalize()
            else:
                # If neither exists, assign an empty string
                record['lastName'] = patient['number']  # or any other default value
                # record['lastName'] = ''

# fill in the 'firstNameOrigin' field
    if check_dictionary_key(patient, 'firstName'):
        record['firstNameOrigin'] = patient['firstName']
    else:
        record['firstNameOrigin'] = ''

    # fill in the 'firstName' field
    if check_dictionary_key(patient, 'firstNameEnglish'):
        record['firstName'] = patient['firstNameEnglish'].capitalize()
    else:
        if check_dictionary_key(patient, 'firstName'):
            # If 'firstNameEnglish' doesn't exist, check 'fullNameEnglish'
            # and assign it to 'firstName' in the record
            record['firstName'] = patient['firstName'].capitalize()
        else:
            # If neither exists, assign an empty string
            record['firstName'] = ''

# age
    if check_dictionary_key(patient, 'age'):
        record['age'] = patient['age']
    else:
        record['age'] = ''

# DOB
    if check_dictionary_key(patient, 'birthDate'):
        record['birthDate'] = patient['birthDate'].strftime("%Y-%m-%d")

# gender
    if check_dictionary_key(patient, 'gender'):
        record['gender'] = patient['gender']
    else:
        record['gender'] = ''

# language
    if check_dictionary_key(patient, 'language'):
        record['language'] = patient['language']
    else:
        record['language'] = ''

# number
    if check_dictionary_key(patient, 'number'):
        numbers = patient['number'].split('-')
        number_counter = '{}'.format(numbers[1][1:] if numbers[1].startswith('0') else numbers[1])
        if len(numbers[0]) >6:
            # Remove the 4th and 5th symbols (index 3 and 4 in zero-based indexing)
            number_normalize = numbers[0][:4] + numbers[0][6:]
            numbers[0] = number_normalize
        # make the correct number
        record['number'] = numbers[0] + '-' + str(number_counter)
    else:
        record['number'] = ''

# status
    if check_dictionary_key(patient, 'status'):
        category_list= { "534261884ca876bb9b7b187a": 'RRV Report Received',
                         "534261804ca876bb9b7b1878": 'INV (Invited)',
                         "534261904ca876bb9b7b187c": 'FAP First application',
                         "5342619b4ca876bb9b7b187e": 'TRE Treated',
                         "534670eed320232052caedc6": 'REF Refused',
                         "541d44d556d27127195639f7": 'EAW Early age',
                         "5469a52d01bc038d04141865": 'PDD Patient died',
                         "54b3c5a2fb4f21a804cba6a5": 'PRF Primary Feedback'}
        status1 = str(patient['status'])
        if status1 in category_list:
            record['status'] = category_list[status1]
            print(f"Status: {category_list[status1]}")
        else:
            record['status'] = ''

    # fill in the 'countre' field
    if check_dictionary_key(patient, '_countries'):
        regex = r"[a-zA-Z][a-zA-Z]" # Regex to match two-letter country codes
        record['country'] = re.search(regex, patient['_countries']).group()
    else:
        record['country'] = ''

#  Phone numbers
    if check_dictionary_key(patient, '_phones'):
        phones = patient['_phones'].split(',')
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

#  Emails
    if check_dictionary_key(patient, '_mails'):
        emails = patient['_mails'].split(',')
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


    return record

            # country = patient['_countries']
            # mails = patient['_mails']
            # phone = patient['_phones']
            # remark = patient['remark']
            # courses = patient['courses']
            # extraInfo = patient['extraInfo']
            # print(f"ID: {id}, Full Name: {fullName}, Full Name English: {fullNameEnglish}, "
            #       f"Last Name: {lastName}, Last Name English: {lastNameEnglish} ")
            # print(f"languages: {languages}, "
            #       f"registered: {registered}, "
            #     f"age: {age}, "
            #     f"number: {number}, courses: {courses} "
            #     f"Country: {country}, Mails: {mails}, Phones: {phone} ")
            # extraInfo_isTranslatorRequired = extraInfo['isTranslatorRequired']
            # extraInfo_extraTesting = extraInfo['extraTesting']
            # extraInfo_isExtraTesting = extraInfo['isExtraTesting']
            # extraInfo_wheelchair = extraInfo['wheelchair']
            # print(f"Is Translator Required: {extraInfo_isTranslatorRequired}, "
            #         f"Extra Testing: {extraInfo_extraTesting}, "
            #         f"Is Extra Testing: {extraInfo_isExtraTesting}, "
            #         f"Wheelchair: {extraInfo_wheelchair}")
            # # print(patient)



def main():
    global client
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

            counter = 0
            # Print each patient document
            for patient in patients:
                record=look_for(patient)
                print(record)
                counter += 1
                if counter >15:
                    break
                # if counter % 1000 == 0:
                #     print(f"Processed {counter} patient records.")
            # print(f"Processed {counter} patient records.")

        except OperationFailure as e:
            print(f"An error occurred while querying the database: {e}")

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
