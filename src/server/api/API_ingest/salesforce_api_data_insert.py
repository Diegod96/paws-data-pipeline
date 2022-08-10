import secrets_dict
from simple_salesforce import Salesforce


def initialize_salesforce_client():
    
    """This function initializes the salesforce client using simple-salesforce library

    Returns:
        simple-salesforce reat api object: simple-salesforce rest api object after authenticating againts salesforce org
    """
    
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
        
def get_record(sf_client):
    contact_record_query_result = sf_client.query("SELECT Id, Name, Facebook_Page__c FROM Contact WHERE Id = '0032g00000Ukx9bAAB'")
    contact_records = contact_record_query_result["records"]
    for contact in contact_records:
        print("Contact Name: " + contact['Name'])
        print("Contact Record Id: " + contact['Id'])
        sf_client.Contact.update(contact['Id'], {'Email': 'test124@test.com'})
        print("Updated Email Successfully")
        

def main():
    sf_client = initialize_salesforce_client()
    get_record(sf_client)
     
if __name__ == "__main__":
    main()