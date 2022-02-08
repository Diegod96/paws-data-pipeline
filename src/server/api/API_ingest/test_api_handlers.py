from config import engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from api.API_ingest import salesforce_api_downloader, salesforce_api_importer
import json

def test_download_salesforce_donation_data():

    #retrieve yesterdays donation data
    data = salesforce_api_downloader.download_donation_data(datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1))
    assert data["attributes"]["reportName"] == "Weston - Donation Report"

def test_import_salesforce_donation_data():
    data = json.load(open("donations.json"))
    Session = sessionmaker(engine)
    session =  Session()
    with session:
        salesforce_api_importer.store_data_in_db(session, data)
        session.rollback()
