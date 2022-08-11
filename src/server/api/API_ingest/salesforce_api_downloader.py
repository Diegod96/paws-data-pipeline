from email import header
import secrets_dict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

import jwt
import requests
import json

from datetime import datetime, timedelta

from flask.globals import current_app

def download_donation_data(start_date, end_date):
    headers = generate_jwt()
    report_filter = json.load(open("report_request.json", "r"))
    
    #override date range
    report_filter["reportMetadata"]["standardDateFilter"]["startDate"] = start_date.strftime("%y-%m-%d")
    report_filter["reportMetadata"]["standardDateFilter"]["endDate"] = end_date.strftime("%y-%m-%d")
    r = requests.post("https://phillypaws.my.salesforce.com/services/data/v37.0/analytics/reports/query", headers=headers, json=report_filter)
    if r.status_code != 200:
        raise Exception("Salesforce API responsded with an error status code: {}".format(r.json()))
    
    data = r.json()
    if(not data["allData"]):
        raise Exception("Date range too large. Full dataset not retrieved")

    return data

def generate_jwt():
    private_key_bytes = bytes(secrets_dict.KEY_PEM, "UTF-8")
    private_key = serialization.load_pem_private_key(
        private_key_bytes, password=None, backend=default_backend()
    )

    encoded_jwt = jwt.encode({
        "iss": secrets_dict.ISS, 
        "sub": secrets_dict.SUB, 
        "aud": secrets_dict.AUD, 
        "exp": datetime.utcnow() + timedelta(seconds=60)}, private_key, algorithm="RS256"
    )

    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": encoded_jwt
    }

    access_token_request = requests.post("https://login.salesforce.com/services/oauth2/token", data=payload)
    response = access_token_request.json()
    access_token = response['access_token']
    bearer_token = 'Bearer ' + access_token
    headers = {'Authorization': bearer_token}
    return headers
