from datetime import datetime
from datetime import timedelta

from flask.globals import current_app

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from config import engine
import json

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import  insert,  Table,  Column, MetaData, exc
from sqlalchemy.dialects.postgresql import Insert

import requests
import re

from requests.models import Response
import secrets_dict


def import_donation_data(start_date, end_date):
    
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
    access_token = access_token_request.json()['access_token']
    bearer_token = 'Bearer ' + access_token
    headers = {'Authorization': bearer_token}

    report_filter = json.load(open("report_request.json", "r"))
    #override date range
    report_filter["reportMetadata"]["standardDateFilter"]["startDate"] = start_date
    report_filter["reportMetadata"]["standardDateFilter"]["endDate"] = end_date
    r = requests.post("https://phillypaws.my.salesforce.com/services/data/v37.0/analytics/reports/query", 
        headers=headers, json=report_filter)
    current_app.logger.info("Fetched data successfully")
    data = r.json()
    if(not data["allData"]):
        raise Exception("Date range too large. Full dataset not retrieved")

    metadata = MetaData()
    sfd  = Table("salesforcedonations", metadata, autoload=True, autoload_with=engine)
    Session = sessionmaker(engine) 
    session =  Session()

    # Stats for import
    dupes = 0
    other_integrity = 0
    other_exceptions = 0
    row_count = 0
    
    rows = data["factMap"]["T!T"]["rows"]
    for row in rows:
        insertable_row = {
            "recurring_donor": row["dataCells"][0]["value"],
            "primary_contact": row["dataCells"][1]["value"],
            "contact_id": row["dataCells"][5]["value"],
            "opp_id": row["dataCells"][6]["value"],
            "amount": row["dataCells"][10]["value"]["amount"],
            "close_date": row["dataCells"][13]["value"],
            "donation_type": row["dataCells"][15]["value"],
            "primary_campaign_source": row["dataCells"][16]["label"]
        }
        stmt = Insert(sfd).values(insertable_row)
        skip_dupes = stmt.on_conflict_do_nothing(
            constraint='uq_donation'
        )
        try:
            result = session.execute(skip_dupes)
        except exc.IntegrityError as e:  # Catch-all for several more specific exceptions
            if  re.match('duplicate key value', str(e.orig) ):
                dupes += 1
                pass
            else:
                other_integrity += 1
                print(e)
        except Exception as e: 
            other_exceptions += 1
            print(e)
    
    session.commit()   # Commit all inserted rows    
    current_app.logger.info("---------------------------------   Stats  -------------------------------------------------")
    current_app.logger.info("Total rows: " + str(row_count) + " Dupes: " + str(dupes))
    current_app.logger.info("Other integrity exceptions: " + str(other_integrity) + " Other exceptions: " + str(other_exceptions))
