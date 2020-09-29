# from flask import current_app
import re


def __clean_csv_headers(header):
    header = re.sub(r'\s\(.*\)', '', header)
    header = re.sub(r'\.+', '_', header.lower().strip().replace(' ', '_').replace('/', '_'))
    return header.replace('#', 'num')


CSV_HEADERS = {
    'petpoint': ['Animal #', 'Outcome Person #', 'Outcome Person Name', 'Out Street Address', 'Out Unit Number',
                 'Out City', 'Out Province', 'Out Postal Code', 'Out Email', 'Out Home Phone', 'Out Cell Phone'],
    'volgistics': ['Last name', 'First name', 'Middle name', 'Number', 'Complete address', 'Street 1', 'Street 2',
                   'Street 3', 'City', 'State', 'Zip', 'All phone numbers', 'Home', 'Work', 'Cell', 'Email'],
    'salesforcecontacts': ['Contact ID', 'First Name', 'Last Name', 'Mailing Street', 'Mailing City',
                           'Mailing State/Province', 'Mailing Zip/Postal Code', 'Mailing Country', 'Phone', 'Mobile',
                           'Email'],
    'volgisticsshifts': ['Number', 'Site', 'Place', 'Assignment', 'Role', 'From', 'To', 'Spare date', 'Spare dropdown',
                         'Spare checkbox', 'Coordinator'],
    'salesforcedonations': ['Recurring donor', 'Opportunity Owner', 'Account Name', 'Opportunity ID (18 Digit)', 'Account ID (18 digit)', 
                            'Opportunity Name', 'Stage', 'Fiscal Period', 'Amount', 'Probability (%)', 'Age',
                            'Close Date', 'Created Date', 'Type', 'Primary Campaign Source',
                            'Source', 'Contact ID (18 Digit)', 'Primary Contact']
}

DATASOURCE_MAPPING = {
    'salesforcecontacts': {
        'id': 'contact_id',
        'csv_names': CSV_HEADERS['salesforcecontacts'],
        'tracked_columns': list(map(__clean_csv_headers, CSV_HEADERS['salesforcecontacts'])),
        'identifying_criteria': [],
        '_label': 'salesforce',
        'table_id': 'contact_id',
        'table_email': 'email',
        '_table_name': ['first_name', 'last_name']
    },
    'volgistics': {
        'id': 'number',
        'csv_names': CSV_HEADERS['volgistics'],
        'tracked_columns': list(map(__clean_csv_headers, CSV_HEADERS['volgistics'])),
        'identifying_criteria': [],
        '_label': 'volgistics',
        'table_id': 'Number'.lower(),
        'table_email': 'Email'.lower(),
        '_table_name': ['first_name', 'last_name'],
        'sheetname': 'Master'
    },
    'petpoint': {
        'id': 'outcome_person_num',
        'csv_names': CSV_HEADERS['petpoint'],
        'tracked_columns': list(map(__clean_csv_headers, CSV_HEADERS['petpoint'])),
        'identifying_criteria': [],
        '_label': 'petpoint',
        'table_id': 'outcome_person_num',  # "Outcome.Person.."
        'table_email': 'out_email',
        '_table_name': ['outcome_person_name']
    },
    'volgisticsshifts': {
        'id': 'number',
        'csv_names': CSV_HEADERS['volgisticsshifts'],
        'tracked_columns': list(map(__clean_csv_headers, CSV_HEADERS['volgisticsshifts'])),
        'identifying_criteria': [],
        '_label': 'volgisticsshifts',
        'table_id': 'number',
        'table_email': None,
        '_table_name': [],
        'sheetname': 'Assignments'
    },
    'salesforcedonations': {
        'id': 'contact_id',
        'csv_names': CSV_HEADERS['salesforcedonations'],
        'tracked_columns': list(map(__clean_csv_headers, CSV_HEADERS['salesforcedonations'])),
        'identifying_criteria': [],
        '_label': 'salesforcedonations',
        'table_id': 'contact_id',
        'table_email': None,
        '_table_name': []
    }
}
