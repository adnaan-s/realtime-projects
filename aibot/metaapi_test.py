import asyncio
import os
from dotenv import load_dotenv
from metaapi_cloud_sdk import MetaApi

load_dotenv()

METAAPI_TOKEN = os.getenv('METAAPI_TOKEN')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

async def test_metaapi_connection():
    api = MetaApi(METAAPI_TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        print(f"Account state: {account.state}")
        
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_connected()
        
        print("Successfully connected to MetaApi")
        
        account_information = await connection.get_account_information()
        print(f"Account Information: {account_information}")
        
        # Try to get the price for EURUSD
        price = await connection.get_symbol_price('EURUSD')
        print(f"EURUSD price: {price}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals():
            await connection.close()

if __name__ == "__main__":
    asyncio.run(test_metaapi_connection())