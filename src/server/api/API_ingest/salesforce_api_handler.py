from datetime import datetime, timedelta

from flask.globals import current_app

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from config import engine

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import  insert,  Table,  Column, MetaData, exc
from sqlalchemy.dialects.postgresql import Insert

from requests.models import Response
from api.API_ingest import salesforce_api_downloader, salesforce_api_importer


def store_salesforce_donation_data(start_date, end_date):
    data = salesforce_api_downloader.download_donation_data(start_date, end_date)
    salesforce_api_importer.import_data(data)
