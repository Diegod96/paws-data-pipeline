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

def main():
    sf_client = initialize_salesforce_client()
     
if __name__ == "__main__":
    main()