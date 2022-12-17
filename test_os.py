#test_os.py

import requests
import os

key = 'TOKEN_BOT'

token = os.getenv(key, default=None) # примерно, точно не помню как
print(token)