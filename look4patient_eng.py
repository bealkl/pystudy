#!/usr/bin/env python3
import re
from collections import OrderedDict
from dictionary_utils import check_dictionary_key
from country_list import country_list
from old_diagnoses import old_diagnoses

def look4patient_eng(patient):

    fields = [
    "first_name",
    "last_name",
    "father_name",
    "email",
    "additional_emails",
    "phone",
    "additional_phones",
    "position",
    "last_contact",
    "birthday",
    "gender",
    "last_update",
    "address",
    "company",
    "company_phone",
    "company_email",
    "country",
    "city",
    "postal_code",
    "region",
    "website",
    "legal_street",
    "legal_city",
    "legal_region",
    "legal_postal_code",
    "legal_country",
    "physical_street",
    "physical_city",
    "physical_region",
    "physical_postal_code",
    "physical_country",
    "longitude",
    "latitude",
    "category",
    "discount_group",
    "main_manager",
    "supplier",
    "patient",
    "personal_manager",
    "code",
    "passport",
    "residence_country",
    "country_code",
    "country_phone_code",
    "region_detailed",
    "father_name_eng",
    "mother_name",
    "age_group",
    "treatment_program",
    "service_provision",
    "diagnosis",
    "diagnosis_description",
    "reference_patients",
    "app_installed",
    "follow_up",
    "mass_mailing",
    "accommodation",
    "additional_questions",
    "territory",
    "personal_code",
    "contract",
    "exclusive_contract",
    "additional_phone",
    "additional_email",
    "additional_contacts"
    ]

    record = OrderedDict()
    for k in fields:
        record[k]= ''

    # fill in the 'lastName' field
    if check_dictionary_key(patient, 'lastNameEnglish'):
        record['last_name'] = patient['lastNameEnglish'].capitalize()
    else:
        if check_dictionary_key(patient, 'fullNameEnglish'):
            # If 'lastNameEnglish' doesn't exist, check 'fullNameEnglish'
            # and assign it to 'lastName' in the record
            record['last_name'] = patient['fullNameEnglish'].capitalize()
        else:
            if check_dictionary_key(patient, 'fullName'):
                # If neither 'lastNameEnglish' nor 'fullNameEnglish' exists,
                # check 'fullName' and assign it to 'lastName' in the record
                record['last_name'] = patient['fullName'].capitalize()
            else:
                # If neither exists, assign an empty string
                record['last_name'] = patient['number']  # or any other default value

    # fill in the 'firstName' field
    if check_dictionary_key(patient, 'firstNameEnglish'):
        record['first_name'] = patient['firstNameEnglish'].capitalize()
    else:
        if check_dictionary_key(patient, 'firstName'):
            # If 'firstNameEnglish' doesn't exist, check 'fullNameEnglish'
             # and assign it to 'firstName' in the record
             record['first_name'] = patient['firstName'].capitalize()
        else:
            # If neither exists, assign an empty string
            record['first_name'] = ''

    # DOB
    if check_dictionary_key(patient, 'birthDate'):
        record['birthday'] = patient['birthDate'].strftime("%Y-%m-%d")

    # gender
    record['gender'] = int(0)  # Default value for
    if check_dictionary_key(patient, 'gender'):
        if patient['gender'].upper().strip() == "M":
            record['gender'] = int(1)
        elif patient['gender'].upper().strip() == "F":
            record['gender'] = int(2)

    # number
    if check_dictionary_key(patient, 'number'):
        try:
            numbers = patient['number'].split('-')
            if len(numbers[1]) <= 0:
                numbers[1] = '888'
            if numbers[1].isdigit():
                numbers[1] = str(int(numbers[1]))  # Convert to integer and back to string to remove leading zeros
            numbers[1] = numbers[1][:-1] + '99' if numbers[1].endswith('a') else numbers[1]
            numbers[0] = numbers[0].strip().replace(' ', '')
            if len(numbers[0]) > 6:
                # Remove the 4th and 5th symbols (index 3 and 4 in zero-based indexing)
                number_normalize = numbers[0][:4] + numbers[0][6:]
                numbers[0] = number_normalize
            # make the correct number
            record['code'] = numbers[0] + '-' + numbers[1]
        except IndexError:
            # Handle the case where split() doesn't produce enough elements
            record['code'] = patient['number']  # Keep original value
        except Exception as e:
            # Handle any other unexpected errors
            print(f"Error processing number {patient['number']}: {str(e)}")
            record['code'] = ''
    else:
        record['code'] = ''
    # print(f"Number: {record['number']}")
    # status
    if check_dictionary_key(patient, 'status'):
        category_list = {"534261884ca876bb9b7b187a": 'RRV Report Received',
                     "534261804ca876bb9b7b1878": 'INV (Invited)',
                     "534261904ca876bb9b7b187c": 'FAP First application',
                     "5342619b4ca876bb9b7b187e": 'TRE Treated',
                     "534670eed320232052caedc6": 'REF Refused',
                     "541d44d556d27127195639f7": 'EAW Early age',
                     "5469a52d01bc038d04141865": 'PDD Patient died',
                     "54b3c5a2fb4f21a804cba6a5": 'PRF Primary Feedback'}
        status1 = str(patient['status'])
        if status1 in category_list:
            record['category'] = category_list[status1]
            # print(f"Status: {category_list[status1]}")
        else:
            record['category'] = ''

    # passport
    record['passport'] = ''
    if check_dictionary_key(patient, 'passports'):
        passports = patient['passports']
        passport_record = ''
        passport_remark=''
        for passport in passports:
            passport_record = ''
            if len(record['passport']) > 0:
                record['passport'] += '; '
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
        record['passport'] += passport_record

    # fill in the 'countre' field
    if check_dictionary_key(patient, '_countries'):
        regex = r"[a-zA-Z][a-zA-Z]"  # Regex to match two-letter country codes
        record['country'] = re.search(regex, patient['_countries']).group()
        record['country'] = country_list.get(record['country'], '')
    else:
        record['country'] = ''

    # partner
    if check_dictionary_key(patient, 'partner_list'):
        record['reference_patients'] = patient['partner_list'].strip().replace('<br />', '; ')
    else:
        record['reference_patients'] = ''

    #  Phone numbers
    if check_dictionary_key(patient, '_phones'):
        phones = patient['_phones'].split(',')
        # Normalize phone numbers by removing spaces and dashes
        # phones = [phone.strip().replace(' ', '').replace('-', '') for phone in phones if phone.strip()]
        record['phone'] = phones[0].strip()
        skip0 = True
        if len(phones) > 1:
            for phone_patient in phones:
                # If there are multiple phone numbers, take the next ones as alternative phones
                if skip0:
                    skip0 = False
                    continue
                record['additional_phones'] = str(phone_patient).strip() + ";"
        else:  # If no phone numbers are found, set to empty strings
            record['additional_phones'] = ''
    else:
        record['phone'] = ''
        record['additional_phones'] = ''

    #  Emails
    if check_dictionary_key(patient, '_mails'):
        emails = patient['_mails'].split(',')
        # Normalize emails by removing spaces
        emails = [email_patient.strip() for email_patient in emails if email_patient.strip()]
        record['email'] = emails[0] if emails else ''
        skip0 = True
        if len(emails) > 1:
            for email_patient in emails:
                # If there are multiple emails, take the next ones as alternative emails
                if skip0:
                    skip0 = False
                    continue
                record['additional_emails'] = str(email_patient).strip() + ";"
        else:  # If no emails are found, set to empty strings
            record['additional_emails'] = ''
    else:
        record['email'] = ''
        record['additional_emails'] = ''

    # Diagnosis
    if check_dictionary_key(patient, 'diagnosis_list'):
        record['diagnosis'] = str(patient['diagnosis_list']).strip().replace("<br />", "; ")
    else:
        record['diagnosis'] = ''

    # Extra diagnosis
    if check_dictionary_key(patient, 'diagnoses'):
        record['diagnosis_description'] = ''
        i = 1
        for diag in patient['diagnoses']:
            record['diagnosis_description'] += " (" + str(i) + ") "
            for key in diag.keys():
                this_key = str(diag[key])
                if key == 'diagnosis':
                    # If the key is 'diagnosis', we have to check if it exists in the old_diagnoses dictionary
                    if check_dictionary_key(old_diagnoses, 'diagnosis'):
                        record['diagnosis_description'] = record['diagnosis_description'] + "; діагноз: " + old_diagnoses[this_key]
                    continue
                if key == '_id':
                    # If the key is '_id', we skip it
                    continue
                if len(this_key) > 0: record['diagnosis_description'] += str(key) + " " + this_key + "; "
            i += 1
    else:
        record['diagnosis_description'] = ''

    # contacts
    if check_dictionary_key(patient, 'contacts'):
        for contact in patient['contacts']:
            address = ''
            if check_dictionary_key(contact, 'country'):
                country = str(contact['country'])
                if len(country) > 1: address += country + "; "
            if check_dictionary_key(contact, 'region'):
                region = str(contact['region'])
                if len(region) > 1: address += region + "; "
            if check_dictionary_key(contact, 'city'):
                city = str(contact['city'])
                if len(city) > 1: address += city + "; "
            if check_dictionary_key(contact, 'index'):
                index = str(contact['index'])
                if len(index) > 1: address += index + "; "
            if check_dictionary_key(contact, 'streetAddress'):
                street_address = str(contact['streetAddress'])
                if len(street_address) > 1: address += street_address + "; "
            if check_dictionary_key(contact, 'emails'):
                for email in contact['emails']:
                    if check_dictionary_key(email, 'address'):
                        email_address = str(email['address']).strip()
                        if len(email_address) > 1:
                            if email_address in record['email']: continue
                            if email_address in record['alt_emails']: continue
                            if len(address) > 0: address += "; "
                            address += email_address
                    if check_dictionary_key(email, 'remark'):
                        email_remark = str(email['remark']).strip().replace("Origin: ", "")
                        if len(email_remark) > 1:
                            if email_remark in record['email']: continue
                            if email_remark in record['alt_emails']: continue
                            if len(address) > 0: address += "; "
                            address += email_remark
            if check_dictionary_key(contact, 'phones'):
                for phone in contact['phones']:
                    if check_dictionary_key(phone, 'number'):
                        phone_kind = ''
                        phone_number = str(phone['number']).strip()
                        if check_dictionary_key(phone, 'kind'):
                            phone_kind = str(phone['kind']).strip()
                            if len(phone_kind) > 1:
                                phone_kind = "(" + phone_kind + ")"
                        if len(phone_number) > 1:
                            if phone_number in record['phone']: continue
                            if phone_number in record['alt_phones']: continue
                            if len(address) > 0: address += "; "
                            address += phone_number + " (" + phone_kind + ")"
                    if check_dictionary_key(phone, 'additional'):
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
        record['treatment_program'] = ''
        for cure_plan in patient['cureplans']:
            if check_dictionary_key(cure_plan, 'beginDate'):
                record['treatment_program'] = record['treatment_program'] + cure_plan['beginDate'].strftime("%Y-%m-%d")
            if check_dictionary_key(cure_plan, 'endDate'):
                record['treatment_program'] = record['treatment_program'] + ".." + cure_plan['endDate'].strftime("%Y-%m-%d")
            if check_dictionary_key(cure_plan, 'bookingWhere'):
                record['treatment_program'] = record['treatment_program'] + ", " + str(cure_plan['bookingWhere']).strip()
            if check_dictionary_key(cure_plan, 'hasBooking'):
                if cure_plan['hasBooking']:
                    record['treatment_program'] = record['treatment_program'] + ", " + "Booking"
                else:
                    record['treatment_program'] = record['treatment_program'] + ", " + "No Booking"
            if check_dictionary_key(cure_plan, 'hasTickets'):
                if cure_plan['hasTickets']:
                    record['treatment_program'] = record['treatment_program'] + ", " + "Tickets"
                else:
                    record['treatment_program'] = record['treatment_program'] + ", " + "No Tickets"
            if check_dictionary_key(cure_plan, 'payment'):
                record['treatment_program'] = record['treatment_program'] + ", payment" + str(cure_plan['payment']).strip()
            if check_dictionary_key(cure_plan, 'remark'):
                record['treatment_program'] = record['treatment_program'] + ", " + str(cure_plan['remark']).strip()
            if len(record['treatment_program']) > 0: record['treatment_program'] = record['treatment_program'] + "; "
    else:
        record['treatment_program'] = ''

    # registered
    if check_dictionary_key(patient, 'remark'):
        record['additional_questions'] = patient['remark']
    else:
        record['additional_questions'] = ''

    # remark
    if check_dictionary_key(patient, 'registered'):
        record['last_update'] = patient['registered'].strftime("%Y-%m-%d")
    else:
        record['last_update'] = ''

    # wheelchair
    if check_dictionary_key(patient, 'extraInfo'):
        if check_dictionary_key(patient['extraInfo'], 'wheelchair'):
            # record['wheelchair'] = patient['extraInfo']['wheelchair']
            if(len(record['additional_questions']) > 0):
                record['additional_questions'] = record['additional_questions'] + "; "
            record['additional_questions'] = "wheelchair: "+ patient['extraInfo']['wheelchair']+ ";"
    #     else:
    #         record['wheelchair'] = ''
    # else:
    #     record['wheelchair'] = ''

    # sourceLetter
    if check_dictionary_key(patient, 'sourceLetter'):
        if(len(record['additional_questions']) > 0):
            record['additional_questions'] = record['additional_questions'] + "; "
        record['additional_questions'] = "sourceLetter: "+ patient['sourceLetter']+"; "
        # record['sourceLetter'] = patient['sourceLetter']
        # record['sourceLetter'] = patient['sourceLetter']
    # else:
    #     record['sourceLetter'] = ''

    # sourceLetterEnglish
    if check_dictionary_key(patient, 'sourceLetterEnglish'):
        if(len(record['additional_questions']) > 0):
            record['additional_questions'] = record['additional_questions'] + "; "
        record['additional_questions'] = "sourceLetterEnglish: "+patient['sourceLetterEnglish']+"; "
    #     record['sourceLetterEnglish'] = patient['sourceLetterEnglish']
    # else:
    #     record['sourceLetterEnglish'] = ''
    
    return record
