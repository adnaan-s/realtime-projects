import asyncio
import logging
import os
from dotenv import load_dotenv
from metaapi_cloud_sdk import MetaApi
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve MetaApi credentials from environment variables
METAAPI_TOKEN = os.getenv('METAAPI_TOKEN')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

# Check if credentials are loaded
if not METAAPI_TOKEN or not ACCOUNT_ID:
    raise ValueError("METAAPI_TOKEN or ACCOUNT_ID not found in environment variables")

# Set up stop-loss and take-profit values
STOP_LOSS_PIPS = 50
TAKE_PROFIT_PIPS = 100

def get_prediction(pair):
    try:
        response = requests.get(f"http://127.0.0.1:5000/forex_predict/{pair}")
        if response.status_code == 200:
            data = response.json()
            return data.get('prediction')
        else:
            logging.error(f"Failed to get prediction for {pair}. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error getting prediction for {pair}: {e}")
        return None

async def open_trade(api, pair, signal):
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        
        if account.state != 'DEPLOYED':
            logging.error(f"Account is not deployed. Current state: {account.state}")
            return

        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_connected()
        
        trade_type = 'ORDER_TYPE_BUY' if signal == 'buy' else 'ORDER_TYPE_SELL'
        
        price = await connection.get_symbol_price(pair)
        if price is None:
            logging.error(f"Could not retrieve market price for {pair}")
            return
        
        market_price = price.ask if trade_type == 'ORDER_TYPE_BUY' else price.bid
        
        stop_loss_price = market_price - STOP_LOSS_PIPS * 0.0001 if trade_type == 'ORDER_TYPE_BUY' else market_price + STOP_LOSS_PIPS * 0.0001
        take_profit_price = market_price + TAKE_PROFIT_PIPS * 0.0001 if trade_type == 'ORDER_TYPE_BUY' else market_price - TAKE_PROFIT_PIPS * 0.0001

        result = await connection.create_market_buy_order(
            pair, 0.01, stop_loss_price, take_profit_price
        ) if trade_type == 'ORDER_TYPE_BUY' else await connection.create_market_sell_order(
            pair, 0.01, stop_loss_price, take_profit_price
        )

        logging.info(f"Opened {trade_type} trade for {pair} at {market_price} with SL: {stop_loss_price}, TP: {take_profit_price}")
        logging.info(f"Trade result: {result}")
    
    except Exception as e:
        logging.error(f"Error opening trade for {pair}: {e}")
    finally:
        if 'connection' in locals():
            await connection.close()

async def execute_trade_for_signals(signals):
    api = MetaApi(METAAPI_TOKEN)
    for pair, signal in signals.items():
        await open_trade(api, pair, signal)

async def main():
    api = MetaApi(METAAPI_TOKEN)
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    
    tasks = [open_trade(api, pair, 'buy') for pair in pairs]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())