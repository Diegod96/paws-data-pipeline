from config import engine
from flask import current_app
import traceback

import pandas as pd
import numpy as np
from datetime import datetime, date
from collections import Counter
import dateutil

def date_difference(my_date, max_date):
    '''
    This function takes in a single date from the donations dataframe (per row) and compares the difference between that date and the date in which matching occurs.
    I.e. pipeline matching should provide a query_date so that this can work.
    '''

    d1 = datetime.strptime(str(my_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(max_date), "%Y-%m-%d")
    diff = (d2 - d1)
    return diff


def create_scores():
    '''
    (used to) require query date as input-- must be string in the following format "%Y-%m-%d"
    returns a list of matching_ids and scores as tuples
    will also insert rfm scores into rfm_scores table----see src/server/api/admin_api.py
    '''
    
    # We calculate query_date below in frequncy

    with engine.connect() as connection:
        current_app.logger.debug("running create_scores()")
        # read in data from database via pull_donations_for_rfm() func (reads in as a list of tuples)
        df = pd.read_sql(
            """
            select pc.matching_id, s.amount, s.close_date 
            from salesforcedonations s 
            inner join pdp_contacts pc on pc.source_id = s.contact_id and pc.source_type = 'salesforcecontacts'
            where pc.archived_date is null order by matching_id
            """
            , connection)
        df = pd.DataFrame(df, columns=['matching_id', 'amount', 'close_date'])

        from api.admin_api import read_rfm_edges,  insert_rfm_scores  # Avoid circular import issues

        rfm_dict = read_rfm_edges()

        if len(rfm_dict) == 3:    #  r,f,m

            try:

                recency_labels = [5,4,3,2,1]
                recency_bins =   list(rfm_dict['r'].values())    #imported from table

                frequency_labels = [1,2,3,4,5]
                frequency_bins  =  list(rfm_dict['f'].values())    #imported from table

                monetary_labels = [1,2,3,4,5]
                monetary_bins =   list(rfm_dict['m'].values())      #imported from table


                ########################## recency #########################################

                donations_past_year = df
                donations_past_year['close_date'] =pd.to_datetime(donations_past_year['close_date']).dt.date

                # calculate date difference between input date and individual row close date

                days = []
                max_close_date = donations_past_year['close_date'].max()
                for ii in donations_past_year['close_date']:
                    days.append(date_difference(ii, max_close_date))
                donations_past_year['days_since'] = days

                grouped_past_year = donations_past_year.groupby('matching_id').agg({'days_since': ['min']}).reset_index()
                print(grouped_past_year.head())
            
                grouped_past_year[('days_since', 'min')]= grouped_past_year[('days_since', 'min')].dt.days

                max_maybe = grouped_past_year[('days_since', 'min')].max()

                real_max = max(max_maybe,  max(recency_bins)+1 )

                recency_bins.append(real_max)


                grouped_past_year['recency_score'] = pd.cut(grouped_past_year[('days_since','min')], bins= recency_bins, labels=recency_labels, include_lowest = True)
                grouped_past_year.rename(columns={('recency_score', ''): 'recency_score'})

                ################################## frequency ###############################

                query_date = df['close_date'].max()

                df['close_date'] = pd.DatetimeIndex(df['close_date'])

                df_grouped = df.groupby(['matching_id', pd.Grouper(key = 'close_date', freq = 'Q')]).count().max(level=0)

                df_freq =  df.loc[df['close_date'] >    pd.Timestamp(query_date) - pd.Timedelta( "365 days")  ]         #pd.DatetimeIndex(df['close_date'] - pd.Timedelta( "30 days")    )

                df_grouped = df_freq.groupby(['matching_id']).count()

                df_grouped = df_grouped.reset_index()

                frequency_bins.append(np.inf)

                df_frequency = df_grouped[['matching_id' , 'amount']] # amount is a placeholder as the groupby step just gives a frequency count, the value doesn't correspond to donation monetary amount.

                df_frequency = df_frequency.rename(columns = {'amount':'frequency'}) #renaming amount to frequency

                df_frequency['frequency_score'] = pd.cut(df_frequency['frequency'],
                                                bins = frequency_bins, labels=frequency_labels, include_lowest=False)
                
                ################################## amount ##################################

                #   Need to score people with R, M but not F as a 1

                monetary_bins.append(np.inf)

                df_amount = df.groupby(df['matching_id'], as_index=False).amount.max()

                df_amount['amount_score'] = pd.cut(df_amount['amount'], bins= monetary_bins, include_lowest=True, labels = monetary_labels)

                # raise ValueError   #  Just to test exception handling

                # Concatenate rfm scores
                    # merge monetary df and frequency df
                df_semi = df_amount.merge(df_frequency, left_on='matching_id', right_on= 'matching_id', how='left')
                print(grouped_past_year.head())
                print(df_semi.head())
                
                df_semi['frequency_score'] = df_semi['frequency_score'].fillna(1)

                df_final = df_semi.merge(grouped_past_year, left_on='matching_id', right_on= 'matching_id', how='left')        # merge monetary/frequency dfs to recency df

                # import function: rfm_concat, which will catenate integers as a string and then convert back to a single integer
                from rfm_funcs.rfm_functions import rfm_concat
                rfm_score = rfm_concat(df_final[('recency_score'), ''], df_final['frequency_score'], df_final['amount_score'])

                # Append rfm score to final df
                df_final['rfm_score'] = rfm_score

                from rfm_funcs.rfm_functions import merge_series
                score_tuples = merge_series((df_final['matching_id']), df_final['rfm_score'])

            except Exception as e:
                current_app.logger.error(e)
                trace_back_string = traceback.format_exc()
                current_app.logger.error(trace_back_string)
                return 0

            try:
                insert_rfm_scores(score_tuples)
            except Exception as e:
                current_app.logger.error(e)
                trace_back_string = traceback.format_exc()
                current_app.logger.error(trace_back_string)
                return 0

            return len(score_tuples)   # Not sure there's anything to do with them at this point

        else:   # Didn't get len == 3
            current_app.logger.error("rfm_edges missing from DB or malformed. Could not perform rfm scoring")
            return 0
