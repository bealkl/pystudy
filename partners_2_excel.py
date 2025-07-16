#!/usr/bin/env python3
# Partners Semantic Analysis
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import re
import pandas as pd
from datetime import datetime


from unicodedata import normalize

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


def partners_semantic_analysis(partner):
    passport_record: str= ''
    record = {'id': str(partner['_id'])}

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
    record['firstName'] = record['firstName'].replace('()','').strip()

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
        skip0 = True
        if len(emails) > 1:
            for email in emails:
                # If there are multiple emails, take the next ones as alternative emails
                if skip0:
                    skip0 = False
                    continue
                record['alt_emails'] = str(email).strip() + ";"
        else:  # If no emails are found, set to empty strings
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
        skip0 = True
        if len(phones) > 1:
            for phone in phones:
                # If there are multiple phone numbers, take the next ones as alternative phones
                if skip0:
                    skip0 = False
                    continue
                record['alt_phones'] = str(phone).strip() + ";"
        else:  # If no phone numbers are found, set to empty strings
            record['alt_phones'] = ''
    else:
        record['phone'] = ''
        record['alt_phones'] = ''

    # code
    if check_dictionary_key(partner, 'code'):
        record['code'] = partner['code'].strip()
    else:
        record['code'] = record['id']  # Use the MongoDB ID as the code if no code is provided

    # territory
    if check_dictionary_key(partner, 'territory'):
        record['territory'] = partner['territory'].strip()
    else:
        record['territory'] = ''

    # contract
    if check_dictionary_key(partner, 'contract'):
        record['contract'] = partner['contract']
    else:
        record['contract'] = False

    # exclusive contract
    if check_dictionary_key(partner, 'exclusiveContract'):
        record['exclusiveContract'] = partner['exclusiveContract']
    else:
        record['exclusiveContract'] = False

    # extra
    if check_dictionary_key(partner, 'extra'):
        record['extra'] = partner['extra']
    else:
        record['extra'] = ''

    # created_at
    if check_dictionary_key(partner, 'created_at'):
        record['created'] = partner['created_at'].strftime("%Y-%m-%d")

    # updated_at - Останні зміни
    if check_dictionary_key(partner, 'updated_at'):
        record['updated'] = partner['updated_at'].strftime("%Y-%m-%d")
    else:
        record['updated'] = record['created']

    # contracts
    if check_dictionary_key(partner, 'contracts'):
        contracts = partner['contracts']
        record['contracts'] = ''
        for contract in contracts:
            contract_record = ''
            if 'name' in contract and len(contract['name']) > 0:
                contract_record = 'name: ' + contract.get('name', '')
            if 'extrainfo' in contract and len(contract['extrainfo']) > 0:
                contract_record = contract_record + ', extrainfo: ' + contract.get('extrainfo', '').replace('\n',', ')
            if 'territory' in contract and len(contract['territory']) > 0:
                contract_record = contract_record + ', territory: ' + contract.get('territory', '')
            if 'beginDate' in contract and contract['beginDate'] is not None:
                contract_record = contract_record + ', begin_date: ' + contract.get('beginDate', '').strftime("%Y-%m-%d")
            if 'endDate' in contract and contract['endDate'] is not None:
                contract_record = contract_record + ', end_date: ' + contract.get('endDate', '').strftime("%Y-%m-%d")
            record['contracts'] = record['contracts'] + contract_record
    else:
        record['contracts'] = ''

    # home
    if check_dictionary_key(partner, 'home'):
        if check_dictionary_key(partner['home'], 'country'):
            record['country']= partner['home']['country'].strip()
        if check_dictionary_key(partner['home'], 'streetAddress'):
            record['streetAddress']= 'Street address: ' + partner['home']['streetAddress'].strip()

    # offices
    if check_dictionary_key(partner, 'offices'):
        for office in partner['offices']:
            # print("-------------------")
            for key in office.keys():
                this_key=str(key)
                if this_key=='emails':
                    values_email = office[key]
                    email_str=''
                    for email in values_email:
                        address = email.get('address','')
                        if address == record['email'] or address in record['alt_emails']:
                            # This email is the same as the main email or an alternative email
                            continue
                        remark = email.get('remark', '')
                        if len(address) >0:
                            email_str += address
                            email_str += '; '
                        if len(remark) > 0:
                            email_str += remark
                            email_str += '; '
                        # print(f"email_: {address}, {remark}, record['email']: {record['email']}, record['alt_emails']: {record['alt_emails']}")
                    # continue
                    if len(email_str) > 0:
                        record['email_office'] = email_str
                if this_key=='phones':
                    values_phone = office[key]
                    normalize_numbers_from_record_phone=''
                    if record['phone'] != '':
                        # Normalize phone numbers from the main phone number
                        numbers_in_phone = re.findall(r'\d+', record['phone'])
                        normalize_numbers_from_record_phone = ''.join(numbers_in_phone)
                    normalize_numbers_from_record_altphone = ''
                    if record['alt_phones'] != '':
                        # Normalize phone numbers from the alternative phone numbers
                        numbers_in_altphone = ''.join(record['alt_phones'])
                        normalize_numbers_from_record_altphone = ''.join(re.findall(r'\d+', numbers_in_altphone))
                    phone_str=''
                    for phone in values_phone:
                        number = phone.get('number', '')
                        if len(number) < 1:
                            continue
                        # print(f"values_phone: {len(values_phone)}  len(number): {len(number)}, number: {number}")
                        numbers_from_number = re.findall(r'\d+', number)
                        normalize_numbers_from_number = ''.join(numbers_from_number)
                        if normalize_numbers_from_number == normalize_numbers_from_record_phone or normalize_numbers_from_number == normalize_numbers_from_record_altphone:
                            # This phone number is the same as the main phone number
                            continue
                        phone_str += number
                        kind = phone.get('kind', '')
                        if len(kind) > 0:
                            phone_str += ' ('+kind+')'
                        remark = phone.get('remark', '')
                        if len(remark) > 0:
                            phone_str += ' ('+remark+')'
                        additional = phone.get('additional', '')
                        if len(additional) > 0:
                            phone_str += ' /'+additional+'/'
                        if len(phone_str) > 1:
                            phone_str += '; '
                    if len(phone_str) > 0:
                        # print(f"phone_str: {phone_str}, len(phone_str): {len(phone_str)}")
                        record['phone_office'] = phone_str
                    # continue
                # this_value=str(office[key])
                # if len(this_value)>0: print(f"{this_key}: {this_value}")
# passport
                record['passports']=''
                if check_dictionary_key(partner, 'passports'):
                    passports = partner['passports']
                    for passport in passports:
                        passport_record = ''
                        if len(record['passports'])> 0:
                            record['passports'] += '; '
                        if check_dictionary_key(passport, 'number'):
                            passport_number = passport['number'].strip()
                            passport_record = passport_number
                        if check_dictionary_key(passport, 'kind'):
                            passport_kind = passport['kind'].strip()
                            passport_record += ' (' + passport_kind + ')'
                        if check_dictionary_key(passport, 'validTo'):
                            passport_valid_to = passport['validTo'].strftime("%Y-%m-%d")
                            passport_record += ', validTo: ' + passport_valid_to
                        if check_dictionary_key(passport, 'remark'):
                            passport_remark = passport['remark'].strip()
                            if len(passport_remark) > 0:
                                passport_record += ', : ' + passport_remark
                        # print(f"{record['code']} - passport_record: {passport_record}")
                        record['passports'] += passport_record









    return record
# end of semantic_analysis function

partners_db = None  # Global variable to hold the MongoDB client


def main():
    global partners_db
    try:
        # Connect to MongoDB
        partners_db = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        partners_db.server_info()

        db = partners_db['emcell']
        partners_collection = db['partners']

        document_count = partners_collection.count_documents({})
        if document_count == 0:
            print("The partners collection is empty")
            return
        else:
            print(f"Found {document_count} documents in the collection")

        try:
            partners = partners_collection.find()
            records = []
            counter = 0

            for partner in partners:
                record_partners = partners_semantic_analysis(partner)
                records.append(record_partners)
                counter += 1
                if counter % 100 == 0:
                    print(f"Processed {counter} partner records.")

            # Create DataFrame from records
            df = pd.DataFrame(records)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"partners_export_{timestamp}.xlsx"

            # Export to Excel
            df.to_excel(filename, index=False)
            print(f"\nExported {counter} records to {filename}")

        except OperationFailure as e:
            print(f"An error occurred while querying the database: {e}")

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        try:
            partners_db.close()
            print("MongoDB connection closed")
        except NameError:
            pass


if __name__ == "__main__":
    main()
