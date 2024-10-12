from starlette.config import Config
from starlette.datastructures import Secret

try:
    Config = Config(".env") # env file note its configration
except FileNotFoundError :
    Config = Config()
    
DATABASE_URL = Config("DATABASE_URL", cast=Secret)
 # in ordrde to make secret / encrypted / privicy
 #encryted main branch databse url
TEST_DATABASE_URL = Config("TEST_DATABASE_URL", cast=Secret)