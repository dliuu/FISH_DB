import json
import psutil

from sqlalchemy import create_engine, Column, Integer, JSON, Float, String, Boolean, Numeric, Time, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from datetime import datetime

from r_bubble_api import BubbleAPI
from schema import Loan, Company, Funding, Disbursement, Contact, Payment, Loan_Application

process = psutil.Process()
Base = declarative_base()


class InsertPostgres:
    def __init__(self, obj: object, hostname: str, username: str, password: str, database: str):
        self.engine = create_engine(f'postgresql://{username}:{password}@{hostname}/{database}')
        self.obj = obj

        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_loan_dict(self, data):
        '''
        inputs: data(str), an input json

        creates a dictionary from an input json (data)
         {
        "_id": "123",
        "created_by": "Alice",
        "created_date": "2023-01-01T00:00:00",
        "modified_date": "2023-01-02T00:00:00",
        "product_type": "Type A",
        "property_fish": "Property A}
        
        where empty columns are omitted
        '''
        result_dict = {}
        mapper = inspect(self.obj)

        if not isinstance(data, dict):
            raise ValueError("Create_Loan_Dict: Input data must be a dictionary")

        # Transform the JSON keys: replace whitespace with '_' and lowercase all letters
        transformed_data = {key.strip().replace(" ", "_").lower(): value for key, value in data.items()}

        for column in mapper.attrs:
            column_name = column.key
            if column_name in transformed_data:
                result_dict[column_name] = transformed_data[column_name]
        

        return result_dict

    def insert_data(self, json_list: str):
        session = None

        try:
            if 'response' in json_list:
                results = json.loads(json_list)['response']['results']
            else:
                results = json_list

            session = self.Session()
            now = datetime.now()

            # Insert or update JSON data into the table
            for data in results:
                json_string = json.dumps(data)
                
                validated_dict = self.create_loan_dict(data)

                # Formats unique_id as month day year hour_uniqueid
                validated_dict['unique_id'] = "1_" + data['_id']

                #Retrieves existing entry
                existing_entry = session.query(self.obj).filter_by(unique_id=validated_dict['unique_id']).first()
                
                if existing_entry:
                    if existing_entry.raw_json == json_string:
                        #If records are the exact same, pass
                        print(f"No changes detected for entry with unique_id: {validated_dict['unique_id']}")
                        continue

                    # Update the existing entry
                    for key, value in validated_dict.items():
                        setattr(existing_entry, key, value)
                    print(f"Updated entry with unique_id: {validated_dict['unique_id']}")

                else:
                    # Insert a new entry
                    validated_dict['raw_json'] = json_string
                    entry = self.obj(**validated_dict)
                    session.add(entry)
                    print(f"Inserted entry with unique_id: {validated_dict['unique_id']}")


            session.commit()
            print("Data inserted/updated successfully")

        except Exception as error:
            print("Error while connecting to PostgreSQL:", error)

        finally:
            if session:
                session.close()
                print("PostgreSQL connection is closed")

    def insert_table(self, url: str, apikey: str, bubble_table: str, schema: object):
        bubble_api = BubbleAPI(url, apikey)

        json_list = bubble_api.GET_all_objects(bubble_table)
        str_json = json.dumps(json_list)

        self.insert_data(str_json)


#__Main__

hostname = 'ls-3a42eaaff9b377bfc04f3e8af74d944d01035147.cktchk5fub2f.us-east-1.rds.amazonaws.com'
username = 'dbmasteruser'
password = 'r4Hnp|I*,+*#uJ-6n10jK(_k5xhXO(c&'
database = 'postgres'

test_url = 'https://ifish.tech/version-test/api/1.1/obj'
apikey = '6102e1e766adb69c863124ac8b059bc7'

#instance = InsertPostgres(Loan_Application, hostname, username, password, database)
#instance.insert_table(test_url, apikey, 'Loan Application', Loan_Application)

instance = InsertPostgres(Loan, hostname, username, password, database)
instance.insert_table(test_url, apikey, 'Loan', Loan)

#instance = InsertPostgres(Payment, hostname, username, password, database)
#instance.insert_table(test_url, apikey, '(FISH) Payments', Payment)

#instance = InsertPostgres(Funding, hostname, username, password, database)
#instance.insert_table(test_url, apikey, '(FISH) Funding', Funding)

#instance = InsertPostgres(Company, hostname, username, password, database)
#instance.insert_table(test_url, apikey, '(FISH) Company', Company)

#instance = InsertPostgres(Disbursement, hostname, username, password, database)
#instance.insert_table(test_url, apikey, '(FISH) Disbursement_new', Disbursement)


'''
bubble_api = BubbleAPI(test_url, apikey)

json_list = bubble_api.GET_all_objects('Loan Application')

processed_json = json.dumps(json_list)
postgres_insert = InsertPostgres(Loan_Application, hostname, username, password, database)
postgres_insert.insert_json_data(processed_json)
'''


print("Total Memory Used: " + str(process.memory_info().rss))
