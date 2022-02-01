from datetime import datetime, timedelta
from api.API_ingest import salesforce_api_downloader


def test_download_salesforce_donation_data():

    #retrieve yesterdays donation data
    data = salesforce_api_downloader.download_donation_data(datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1))
    assert data["attributes"]["reportName"] == "Weston - Donation Report"