#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import OperationFailure
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
    record= {'id': patient['_id']}

    # fill in the 'lastNameOrigin' field
    if check_dictionary_key(patient, 'lastName'):
        record['lastNameOrigin'] = patient['lastName']
    else:
        record['lastNameOrigin'] = ''

    # fill in the 'lastName' field
    if check_dictionary_key(patient, 'lastNameEnglish'):
        record['lastName'] = patient['lastNameEnglish']
    else:
        if check_dictionary_key(patient, 'fullNameEnglish'):
            # If 'lastNameEnglish' doesn't exist, check 'fullNameEnglish'
            # and assign it to 'lastName' in the record
            record['lastName'] = patient['fullNameEnglish']
        else:
            if check_dictionary_key(patient, 'fullName'):
                # If neither 'lastNameEnglish' nor 'fullNameEnglish' exists,
                # check 'fullName' and assign it to 'lastName' in the record
                record['lastName'] = patient['fullName']
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
        record['firstName'] = patient['firstNameEnglish']
    else:
        if check_dictionary_key(patient, 'firstName'):
            # If 'firstNameEnglish' doesn't exist, check 'fullNameEnglish'
            # and assign it to 'firstName' in the record
            record['firstName'] = patient['firstName']
        else:
            # If neither exists, assign an empty string
            record['firstName'] = ''

    if check_dictionary_key(patient, 'age'):
        record['age'] = patient['age']
    else:
        record['age'] = ''

    if check_dictionary_key(patient, 'gender'):
        record['gender'] = patient['gender']
    else:
        record['gender'] = ''

    if check_dictionary_key(patient, 'language'):
        record['language'] = patient['language']
    else:
        record['language'] = ''

    if check_dictionary_key(patient, 'number'):
        number1 = patient['number']
        print(f"Number before: {number1} ")
        numbers = number1.split('-')
        print(numbers)
        number_counter = int(numbers[1])
        if len(numbers[0]) >6:
            # Remove the 4th and 5th symbols (index 3 and 4 in zero-based indexing)
            number_normalize = numbers[0][:4] + numbers[0][6:]
            numbers[0] = number_normalize

        record['number'] = numbers[0] + '-' + str(number_counter)
        print(f"Number after: {record['number']} ")
    else:
        record['number'] = ''


    return record

            # country = patient['_countries']
            # mails = patient['_mails']
            # phone = patient['_phones']
            # remark = patient['remark']
            # gender = patient['gender']
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
            # break



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
                if counter >10:
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
