from this import d
import secrets_dict
from simple_salesforce import Salesforce

# Download donations that were closed
def download_saleforce_donation_data(start_date, end_date, sf_client):
    print("Downloading Salesforce donation data...")
    donations = sf_client.query_all_iter(format_soql("SELECT Id, Name, Account_Name__c, Primary_Contact__c, Age, Amount, Type, CloseDate FROM Opportunity WHERE CloseDate = {close_date}", close_date=end_date))
    for donation in donations:
        print("Current donation: %s" % donation)
        process_donation(donation)
        
# TODO: Add logic on how we are processing donations
def process_donation(donation):
    pass
        
    
    
    