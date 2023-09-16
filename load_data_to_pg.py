import os
import json
import psycopg2
from get_env import get_env_data_as_dict

env = get_env_data_as_dict('/usr/project_rs_monitor/.env')

db_params = {
    'dbname': env["PG_DB_NAME"],
    'user': env["PG_USER"],
    'password': env["PG_PWD"],
    'host': '127.0.0.1',
    'port': '5432',
}

connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

test_folder_id=1694798857
test_folder_path=f'/usr/project_rs_monitor/data/landing/oglasi/sale/{str(test_folder_id)}/'
data_files_dir = os.listdir(test_folder_path)
data_files_list=[file for file in data_files_dir if file.endswith('.json')]

test_file_path=data_files_list[1]

test_file_full_path=os.path.join(test_folder_path, test_file_path)

with open(test_file_full_path, 'r') as json_file:
    json_data = json.load(json_file)

sql_query = f"INSERT INTO dev.ads_demo (source_directory_id, ad_json) VALUES ({str(test_folder_id)}, '{json.dumps(json_data)}');"


cursor.execute(sql_query)
connection.commit()