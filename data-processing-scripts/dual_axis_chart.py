import csv
import os
from datetime import datetime
from collections import defaultdict
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
outputPath = '../data/commercial_expenditures_occupancy.csv'

absolute_path = os.path.abspath(os.getenv('PUBS_DATA_PATH'))
print("PUBS absolute path is " + os.path.abspath(os.getenv('PUBS_DATA_PATH')))
print("Restaurants absolute path is " + os.path.abspath(os.getenv('RESTAURANTS_DATA_PATH')))

cols = ['pubId', 'buildingId']
pubs_df = pd.read_csv(os.getenv('PUBS_DATA_PATH'), usecols=cols)
pubs_df['commercialType'] = 'Pub'
pubs_df.rename(columns={'pubId': 'commercialId'}, inplace=True)

cols = ['restaurantId', 'buildingId']
restaurants_df = pd.read_csv(os.getenv('RESTAURANTS_DATA_PATH'), usecols=cols)
restaurants_df['commercialType'] = 'Restaurant'
restaurants_df.rename(columns={'restaurantId': 'commercialId'}, inplace=True)

cols = ['employerId', 'buildingId']
employer_df = pd.read_csv(os.getenv('EMPLOYERS_DATA_PATH'), usecols=cols)
employer_df['commercialType'] = 'Work'
employer_df.rename(columns={'employerId': 'commercialId'}, inplace=True)

combined_df = pd.concat([pubs_df, restaurants_df, employer_df], ignore_index=True)
combined_df.drop(['buildingId'], axis=1, inplace=True)

print(combined_df)

cols = ['participantId', 'travelEndLocationId', 'checkInTime', 'startingBalance', 'endingBalance']
travel_journal_df = pd.read_csv(os.getenv('TRAVEL_JOURNAL_DATA_PATH'), usecols=cols)
travel_journal_df = travel_journal_df[travel_journal_df['travelEndLocationId'].isin(combined_df['commercialId'])]
travel_journal_df['start_time'] = pd.to_datetime(travel_journal_df['checkInTime'].str[:-1])
travel_journal_df['month'] = travel_journal_df['start_time'].dt.strftime('%B')
travel_journal_df['day_of_week'] = travel_journal_df['start_time'].dt.strftime('%A')
travel_journal_df['portion_of_day'] = pd.cut(travel_journal_df['start_time'].dt.hour, bins=[0,12,14,18,24], labels=['morning', 'afternoon', 'evening', 'night'], include_lowest=True)
travel_journal_df.rename(columns={'travelEndLocationId': 'commercialId'}, inplace=True)
travel_journal_df['expenditures'] = travel_journal_df['startingBalance'] - travel_journal_df['endingBalance']

#travel_journal_df['occupancy'] = travel_journal_df.groupby('commercialId')['participantId'].transform('count')
travel_journal_df.drop(['startingBalance', 'endingBalance', 'checkInTime'], axis=1, inplace=True)
#print(travel_journal_df)

merged_df = pd.merge(travel_journal_df, combined_df, on='commercialId', how='inner')
merged_df.to_csv(outputPath, index=False)
merged_df.to_json('../data/commercial_expenditures_occupanc.json', orient='records', lines=True)


#distinct_occupancy = merged_df['occupancy'].unique()
#distinct_df = merged_df[['commercialId', 'commercialType', 'occupancy']].drop_duplicates()
#distinct_df = distinct_df.reset_index(drop=True)
# grouped_df = merged_df.groupby(['commercialId'])['expenditures'].sum().reset_index()
# print(grouped_df)
