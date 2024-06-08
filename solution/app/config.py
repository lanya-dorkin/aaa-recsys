import os


db_user = os.environ['POSTGRES_USER']
db_pass = os.environ['POSTGRES_PASSWORD']
db_host = os.environ['POSTGRES_HOST']
db_name = os.environ['POSTGRES_DB']
db_port = os.environ['POSTGRES_PORT']
DB_ADDRESS = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
