import os
import json
from sqlalchemy import create_engine
from get_env import get_env_data_as_dict

env = get_env_data_as_dict('/usr/project_rs_monitor/.env')
engine = create_engine(f'postgresql+psycopg2://{env["PG_USER"]}:{env["PG_PWD"]}@127.0.0.1/{env["PG_DB_NAME"]}')
connection = engine.connect()

test_folder_path='/usr/project_rs_monitor/data/landing/oglasi/sale/1694798857/'
data_files_dir = os.listdir(test_folder_path)
data_files_list=[file for file in data_files_dir if file.endswith('.json')]

test_file_path=data_files_list[0]

test_file_full_path=os.path.join(test_folder_path, test_file_path)

with open(test_file_full_path, 'r') as json_file:
    json_data = json.load(json_file)

db_params = {
    'dbname': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port',
}