from flask.globals import current_app
from api.API_ingest import shelterluv_api_handler, salesforce_api_handler
from datetime import date, timedelta

def start():
    current_app.logger.info("Start Fetching raw data from different API sources")
    #Run each source to store the output in dropbox and in the container as a CSV
    shelterluv_api_handler.store_shelterluv_people_all()
    current_app.logger.info("Successfully fetched data from Shelterluv")
    #retrieve the donation data for yesterday
    start_date = date.today() - timedelta(days=1)
    end_date = start_date
    salesforce_api_handler.store_salesforce_donation_data(start_date, end_date)
    current_app.logger.info("Successfully fetched donation data from Salesforce")