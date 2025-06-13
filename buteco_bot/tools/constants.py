import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BALANCE_API_URL = os.getenv('BALANCE_API_URL', 'http://balance-api:5000')
CLIENT_API_URL = os.getenv('CLIENT_API_URL', 'http://client-api:5000')
COIN_API_URL = os.getenv('COIN_API_URL', 'http://coin-api:5000')
BET_API_URL = os.getenv('BET_API_URL', 'http://bet-api:5000')
AI_API_URL = os.getenv('AI_API_URL', 'http://ai-api:8080')
