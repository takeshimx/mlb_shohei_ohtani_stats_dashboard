import psycopg2
import psycopg2.extras
import pandas as pd
from sqlalchemy import create_engine
from os import listdir
from os.path import isfile, join
import glob

# CONSTANT variables
HOSTNAME = "localhost"
DATABASE = "sampletksmdb"
USERNAME = "postgres"
PWD = "tksm9652"
PORT_ID = 5432

conn = None

# create an engine to my database
engine = create_engine(
    "postgresql://{}:{}@{}:5432/{}".format(USERNAME, PWD, HOSTNAME, DATABASE)
)

# use context manager, WITH clause to connect to the database and to open the cursor
# advantages for using WITH caluse
# 1) take care of closing the cursor
# 2) no need to mention to commit the databasse transactions

# files paths
pitching_files_path = "./data/pitching"
batting_files_path = "./data/batting"


# function for creating file list
def file_list(file_path):
    files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    file_list = [file_path + "/" + f2 for f2 in files]
    return file_list


# glob.glob(pitching_files_path + "/*.csv")

files_to_load = file_list(pitching_files_path) + file_list(batting_files_path)

try:
    # create connect with parameters given
    with psycopg2.connect(
        host=HOSTNAME, dbname=DATABASE, user=USERNAME, password=PWD, port=PORT_ID
    ) as conn:
        # create cursor
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            for f in files_to_load:
                # import csv file to create a dataframe
                data = pd.read_csv(f, index_col=0)
                # extract a name as a table name
                table_name = f.split("/")[-1][:-4]

                # convert df to sql table
                data.to_sql(
                    f"{table_name}",  # table name
                    engine,
                    schema=None,
                    index=False,
                    if_exists="replace",
                )


except Exception as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
