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

test_folder_id=1695755498
test_folder_path=f'/usr/project_rs_monitor/data/landing/oglasi/sale/{str(test_folder_id)}/'
data_files_dir = os.listdir(test_folder_path)
data_files_list=[file for file in data_files_dir if file.endswith('.json')]

quarantine_path='/usr/project_rs_monitor/data/quarantine/oglasi/sale/'

num_files_proc=0

for i in data_files_list:

    test_file_path=i
    test_file_full_path=os.path.join(test_folder_path, test_file_path)

    try:

        with open(test_file_full_path, 'r') as json_file:
            # print(test_file_full_path)
            json_data = json.load(json_file)
            
        # this works if json_data is a dict, not a string repr of json'
        sql_query = f"INSERT INTO dev.ads_demo (source_directory_id, ad_json) VALUES ({str(test_folder_id)}, '{json.dumps(json_data, ensure_ascii=False)}');"

        # cursor.execute("INSERT INTO dev.ads_demo (source_directory_id, ad_json) VALUES (%s, %s::json)", (str(test_folder_id),json_data))

        cursor.execute(sql_query)
        connection.commit()

    except (psycopg2.errors.SyntaxError,json.decoder.JSONDecodeError):
        cursor.execute('ROLLBACK')
        connection.commit()
        # print(f'error parsing file {i}')

        # new_file_path = os.path.join(quarantine_path, os.path.basename(test_file_full_path))
        # os.rename(test_file_full_path, new_file_path)

        os.replace(test_file_full_path, quarantine_path)
        print(f'moved {test_file_path} to quarantine')
    # if num_files_proc == 500:
    #     break
    # else:
    #     num_files_proc+=1