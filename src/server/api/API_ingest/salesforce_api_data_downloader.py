import secrets_dict
import pytz
import datetime

from simple_salesforce import Salesforce, format_soql


def get_updated_contact_record_ids(sf_client):
    """
    The get_updated_contact_record_ids function returns a list of contact record ids that have been updated in
    Salesforce since a predefined time delta. This is done by querying for all Contact records updated within the
    predefined time delta.

    :param sf_client: Make the api call to salesforce
    :return: A list of contact record ids that have been updated in salesforce within the last 10 days
    :doc-author: Diego Delgado
    """
    sf_end_date = datetime.datetime.now(pytz.UTC)
    updated_contact_record_ids_dict = sf_client.Contact.updated(sf_end_date - datetime.timedelta(days=10), sf_end_date)
    updated_contact_record_ids_list = updated_contact_record_ids_dict["ids"]
    return updated_contact_record_ids_list


def gather_contacts_donations(record_ids, sf_client):
    """
    The gather_contacts_donations function takes a list of Salesforce Opportunity record IDs and returns a list of dictionaries.
    Each dictionary in the returned list contains information about one donation, including:
    - The name of the contact who made the donation (npsp__Primary_Contact__c)
    - The amount donated (Amount)
    - The date when they donated (CloseDate)

    :param record_ids: Pass in the list of contact ids that we want to query for
    :param sf_client: Access the salesforce api
    :return: A list of dictionaries
    :doc-author: Diego Delgado
    """
    result_dictionary = sf_client.query(format_soql("SELECT Id,Name, AccountId, npsp__Primary_Contact__c, CloseDate, "
                                                    "Amount, Type, StageName FROM Opportunity WHERE "
                                                    "npsp__Primary_Contact__c IN {ids}", ids=record_ids))
    donations = result_dictionary["records"]
    return donations


def gather_contact_data(start_date, end_date, sf_client):
    """
    The gather_contact_data function gathers all the donations made by contacts in Salesforce
    between a specified start and end date. It returns a list of dictionaries, where each dictionary
    represents one donation record.

    :param start_date: Specify the date to start collecting data from
    :param end_date: Specify the end date for the query
    :param sf_client: Make calls to the salesforce api
    :return: A list of dictionaries, each dictionary representing a single donation
    :doc-author: Diego Delgado
    """
    record_ids = get_updated_contact_record_ids(sf_client)
    donations = gather_contacts_donations(record_ids, sf_client)
    return donations
