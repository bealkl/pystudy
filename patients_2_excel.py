#!/usr/bin/env python3
#!/usr/bin/env python3
from datetime import datetime

import pandas as pd
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
            # print(f"Status: {category_list[status1]}")
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

    # Diagnosis
    if check_dictionary_key(patient, 'diagnosis_list'):
        record['diagnosis'] = str(patient['diagnosis_list']).strip().replace("<br />","; ")
    else:
        record['diagnosis'] = ''

    # Extra diagnosis
    if check_dictionary_key(patient, 'diagnoses'):
        record['extraDiagnosis']= ''
        i=1
        for diag in patient['diagnoses']:
            record['extraDiagnosis']+= " ("+str(i)+") "
            for key in diag.keys():
                this_key=str(diag[key])
                if key == 'diagnosis':
                    # If the key is 'diagnosis', we have to check if it exists in the old_diagnoses dictionary
                    if check_dictionary_key(old_diagnoses, 'diagnosis'):
                        record['extraDiagnosis'] = record['extraDiagnosis']+"; діагноз: "+ old_diagnoses[this_key]
                    continue
                if key == '_id':
                    # If the key is '_id', we skip it
                    continue
                if len(this_key)>0: record['extraDiagnosis']+= str(key) + " " + this_key + "; "
            i+=1
    #        print(f"record['extraDiagnosis']: {record['extraDiagnosis']}")
    else:
        record['extraDiagnosis'] = ''

    # contacts
    if check_dictionary_key(patient, 'contacts'):
        for contact in patient['contacts']:
            address = ''
            if check_dictionary_key(contact,'country'):
                country=str(contact['country'])
                if len(country)>1: address+=country+"; "
            if check_dictionary_key(contact,'region'):
                region=str(contact['region'])
                if len(region)>1: address+=region+"; "
            if check_dictionary_key(contact,'city'):
                city=str(contact['city'])
                if len(city)>1: address+=city+"; "
            if check_dictionary_key(contact,'index'):
                index=str(contact['index'])
                if len(index)>1: address+=index+"; "
            if check_dictionary_key(contact,'streetAddress'):
                street_address=str(contact['streetAddress'])
                if len(street_address)>1: address+=street_address+"; "
            if check_dictionary_key(contact,'emails'):
                for email in contact['emails']:
                    if check_dictionary_key(email,'address'):
                        email_address = str(email['address']).strip()
                        if len(email_address) > 1:
                            if email_address in record['email']: continue
                            if email_address in record['alt_emails']: continue
                            if len(address) > 0: address += "; "
                            address += email_address
                    if check_dictionary_key(email,'remark'):
                        email_remark = str(email['remark']).strip().replace("Origin: ", "")
                        if len(email_remark) > 1:
                            if email_remark in record['email']: continue
                            if email_remark in record['alt_emails']: continue
                            if len(address) > 0: address += "; "
                            address += email_remark
            if check_dictionary_key(contact,'phones'):
                for phone in contact['phones']:
                    if check_dictionary_key(phone,'number'):
                        phone_kind = ''
                        phone_number = str(phone['number']).strip()
                        if check_dictionary_key(phone,'kind'):
                            phone_kind = str(phone['kind']).strip()
                            if len(phone_kind) > 1:
                                phone_kind = "("+phone_kind+")"
                        if len(phone_number) > 1:
                            if phone_number in record['phone']: continue
                            if phone_number in record['alt_phones']: continue
                            if len(address) > 0: address += "; "
                            address += phone_number+ " ("+phone_kind+")"
                    if check_dictionary_key(phone,'additional'):
                        phone_remark = str(phone['additional']).strip().replace("Original: ", "")
                        if len(phone_remark) > 1:
                            if phone_remark in record['phone']: continue
                            if phone_remark in record['alt_phones']: continue
                            if len(address) > 0: address += "; "
                            address += phone_remark
            record['contacts'] = address.strip().replace("; ; ", ";")
    else:
        record['contacts'] = ''

    # courses
    if check_dictionary_key(patient, 'courses'):
        record['courses'] = ''
        for course in patient['courses']:
            if check_dictionary_key(course, 'courseBegin'):
                record['courses'] = record['courses'] + course['courseBegin'].strftime("%Y-%m-%d")
            if check_dictionary_key(course, 'courseEnd'):
                record['courses'] = record['courses'] + ".." + course['courseEnd'].strftime("%Y-%m-%d")
            if check_dictionary_key(course, 'remark'):
                record['courses'] = record['courses'] + ", " + str(course['remark']).strip().replace("Original ", "")
            if len(record['courses']) > 0: record['courses'] = record['courses'] + "; "
    else:
        record['courses'] = ''

    # cureplans
    if check_dictionary_key(patient, 'cureplans'):
        record['cureplans'] = ''
        for cureplan in patient['cureplans']:
            if check_dictionary_key(cureplan, 'beginDate'):
                record['cureplans'] = record['cureplans'] + cureplan['beginDate'].strftime("%Y-%m-%d")
            if check_dictionary_key(cureplan, 'endDate'):
                record['cureplans'] = record['cureplans'] +".."+ cureplan['endDate'].strftime("%Y-%m-%d")
            if check_dictionary_key(cureplan, 'bookingWhere'):
                record['cureplans'] = record['cureplans'] + ", " + str(cureplan['bookingWhere']).strip()
            if check_dictionary_key(cureplan, 'hasBooking'):
                if cureplan['hasBooking']:
                    record['cureplans'] = record['cureplans'] + ", " + "Booking"
                else:
                    record['cureplans'] = record['cureplans'] + ", " + "No Booking"
            if check_dictionary_key(cureplan, 'hasTickets'):
                if cureplan['hasTickets']:
                    record['cureplans'] = record['cureplans'] + ", " + "Tickets"
                else:
                    record['cureplans'] = record['cureplans'] + ", " + "No Tickets"
            if check_dictionary_key(cureplan, 'payment'):
                record['cureplans'] = record['cureplans'] + ", payment" + str(cureplan['payment']).strip()
            if check_dictionary_key(cureplan, 'remark'):
                record['cureplans'] = record['cureplans'] + ", " + str(cureplan['remark']).strip()
            if len(record['cureplans']) > 0: record['cureplans'] = record['cureplans'] + "; "
    else:
        record['cureplans'] = ''

    # registered
    if check_dictionary_key(patient, 'remark'):
        record['remark'] = patient['remark']
    else:
        record['remark'] = ''

    # remark
    if check_dictionary_key(patient, 'registered'):
        record['registered'] = patient['registered'].strftime("%Y-%m-%d")
    else:
        record['registered'] = ''


    # wheelchair
    if check_dictionary_key(patient, 'extraInfo'):
        if check_dictionary_key(patient['extraInfo'], 'wheelchair'):
            record['wheelchair'] = patient['extraInfo']['wheelchair']
        else:
            record['wheelchair'] = ''
    else:
        record['wheelchair'] = ''

    return record



def main():
    global client
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['emcell']
        patients_collection = db['patients']

        document_count = patients_collection.count_documents({})
        if document_count == 0:
            print("The patients collection is empty")
            return
        else:
            print(f"Found {document_count} documents in the collection")

        try:
            # Read all documents from the patients collection
            patients = patients_collection.find()

            # List to store all patient records
            all_records = []
            counter = 0

            # Process each patient document
            for patient in patients:
                record_patients = look_for(patient)
                print(record_patients)
                print(f"Processing patient {counter + 1} with ID: {record_patients['id']}")
                all_records.append(record_patients)
                counter += 1
                # if counter % 100 == 0:
                #     print(f"Processed {counter} patient records.")

            # Create DataFrame from records
            df = pd.DataFrame(all_records)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f'patients_export_{timestamp}.xlsx'

            # Save to Excel
            df.to_excel(excel_filename, index=False)
            print(f"\nProcessed {counter} patient records.")
            print(f"Data exported successfully to {excel_filename}")

        except OperationFailure as e:
            print(f"An error occurred while querying the database: {e}")

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