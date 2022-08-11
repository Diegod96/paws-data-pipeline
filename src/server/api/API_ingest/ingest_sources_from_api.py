from flask.globals import current_app
import salesforce_api_handler
from datetime import date, timedelta, datetime
import pytz

def start():
    # current_app.logger.info("Start Fetching raw data from different API sources")
    #Run each source to store the output in dropbox and in the container as a CSV
    #shelterluv_api_handler.store_shelterluv_people_all()
    # current_app.logger.info("Successfully fetched data from Shelterluv")
    #TODO move this into property file
    print("Fetching donation data from Salesforce...")
    current_date = datetime.now(pytz.timezone('US/EASTERN'))
    start_date = current_date - timedelta(days=1)
    end_date = start_date
    salesforce_api_handler.store_salesforce_donation_data(start_date, end_date)
    print("Successfully fetched donation data from Salesforce!")
    # current_app.logger.info("Successfully fetched donation data from Salesforce")
    
if __name__ == "__main__":
    start()
