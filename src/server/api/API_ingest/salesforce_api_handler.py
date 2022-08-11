
import secrets_dict
from simple_salesforce import Salesforce
import salesforce_api_data_downloader

# Initialize Salesforce client using simple_salesforce library
def initialize_salesforce_client():
    print ("Initializing Salesforce client...")
    try:    
        sf = Salesforce(username=secrets_dict.SALESFORCE_USERNAME,
                    password=secrets_dict.SALESFORCE_PW, 
                    security_token=secrets_dict.SALESFORCE_SECURITY_TOKEN,
                    domain='test',
                    organizationId=secrets_dict.SALESFORCE_ORG_ID
                    )
        print("Salesforce client initialized successfully!")
        return sf
    except Exception as e:
        print("Error occurred while initializing salesforce client: " + str(e))

# Store Salesforce donation data within a given start and end date
def store_salesforce_donation_data(start_date, end_date):
    print("Start Date: %s" % start_date)
    print("End Date: %s" % end_date)
    sf_client = initialize_salesforce_client()
    data = salesforce_api_data_downloader.salesforce_api_data_downloader(start_date, end_date, sf_client)
    

# from datetime import datetime, timedelta

# from flask.globals import current_app

# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.backends import default_backend

# from config import engine

# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import  insert,  Table,  Column, MetaData, exc
# from sqlalchemy.dialects.postgresql import Insert

# from requests.models import Response
# from api.API_ingest import salesforce_api_downloader, salesforce_api_importer


# def store_salesforce_donation_data(start_date, end_date):
#     data = salesforce_api_downloader.download_donation_data(start_date, end_date)
#     salesforce_api_importer.import_data(data)

