from config import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table,  MetaData, exc
from sqlalchemy.dialects.postgresql import Insert
from flask.globals import current_app
import re

def import_data(data):
    Session = sessionmaker(engine) 
    session =  Session()
    with session:
        results = store_data_in_db(session,data)
        session.commit()
    print(results)
    current_app.logger.info("---------------------------------   Stats  -------------------------------------------------")
    current_app.logger.info("Total rows: " + str(results["row_count"]) + " Dupes: " + str(results["dupes"]))
    current_app.logger.info("Other integrity exceptions: " + str(results["other_integrity"]) + " Other exceptions: " + str(results["other_exceptions"]))
    

def store_data_in_db(session, data):
    metadata = MetaData()
    sfd  = Table("salesforcedonations", metadata, autoload=True, autoload_with=engine)
    
    # Stats for import
    dupes = 0
    other_integrity = 0
    other_exceptions = 0
    row_count = 0
    
    rows = data["factMap"]["T!T"]["rows"]
    for row in rows:
        row_count += 1
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
                current_app.logger.error(e)
        except Exception as e: 
            other_exceptions += 1
            current_app.logger.error(e)
    

    return {
        "row_count": row_count,
        "dupes": dupes,
        "other_integrity": other_integrity,
        "other_exceptions": other_exceptions
    }
    