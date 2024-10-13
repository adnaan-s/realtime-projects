import asyncio
import logging
import os
from dotenv import load_dotenv
from metaapi_cloud_sdk import MetaApi
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Retrieve MetaApi credentials from environment variables
METAAPI_TOKEN = os.getenv('METAAPI_TOKEN')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

# Check if credentials are loaded
if not METAAPI_TOKEN or not ACCOUNT_ID:
    raise ValueError("METAAPI_TOKEN or ACCOUNT_ID not found in environment variables")

# Set up stop-loss and take-profit values
STOP_LOSS_PIPS = 50
TAKE_PROFIT_PIPS = 100

async def open_trade(api, account, pair, signal):
    try:
        logger.info(f"Attempting to open trade for {pair} with signal {signal}")
        
        if account.state != 'DEPLOYED':
            logger.error(f"Account is not deployed. Current state: {account.state}")
            return f"Error: Account not deployed. State: {account.state}"

        connection = account.get_streaming_connection()
        await connection.connect()
        
        logger.info("Waiting for connection to be synchronized")
        await connection.wait_synchronized()

        trade_type = 'ORDER_TYPE_BUY' if signal == 'buy' else 'ORDER_TYPE_SELL'
        
        logger.info(f"Fetching symbol price for {pair}")
        price = await connection.get_symbol_price(pair)
        if price is None:
            logger.error(f"Could not retrieve market price for {pair}")
            return f"Error: Could not retrieve market price for {pair}"
        
        market_price = price.ask if trade_type == 'ORDER_TYPE_BUY' else price.bid
        
        logger.info("Calculating trade parameters")
        equity = await connection.get_account_information()
        risk_percentage = 0.01  # 1% risk per trade
        pip_value = 0.0001  # Assuming 4 decimal places for Forex pairs
        lot_size = round((equity.balance * risk_percentage) / (STOP_LOSS_PIPS * pip_value), 2)
        
        stop_loss_price = market_price - STOP_LOSS_PIPS * pip_value if trade_type == 'ORDER_TYPE_BUY' else market_price + STOP_LOSS_PIPS * pip_value
        take_profit_price = market_price + TAKE_PROFIT_PIPS * pip_value if trade_type == 'ORDER_TYPE_BUY' else market_price - TAKE_PROFIT_PIPS * pip_value

        logger.info(f"Executing {trade_type} trade for {pair}")
        result = await connection.create_market_buy_order(
            pair, lot_size, stop_loss_price, take_profit_price
        ) if trade_type == 'ORDER_TYPE_BUY' else await connection.create_market_sell_order(
            pair, lot_size, stop_loss_price, take_profit_price
        )

        logger.info(f"Trade executed: {trade_type} trade for {pair} at {market_price} with SL: {stop_loss_price}, TP: {take_profit_price}, Lot Size: {lot_size}")
        logger.info(f"Trade result: {result}")
        return f"Trade executed: {trade_type} for {pair}"
    
    except Exception as e:
        logger.error(f"Error opening trade for {pair}: {e}")
        return f"Error opening trade for {pair}: {str(e)}"
    finally:
        if 'connection' in locals():
            await connection.close()

async def execute_trade_for_signals(signals):
    logger.info(f"Executing trades for signals: {signals}")
    api = MetaApi(METAAPI_TOKEN)
    
    try:
        logger.info("Fetching MetaAPI account")
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        
        logger.info("Ensuring account is deployed")
        if account.state != 'DEPLOYED':
            logger.info("Account is not deployed. Deploying now...")
            await account.deploy()
        
        logger.info("Waiting for account to be deployed")
        await account.wait_deployed()
        
        results = []
        for pair, signal in signals.items():
            logger.info(f"Processing trade for {pair} with signal {signal}")
            result = await open_trade(api, account, pair, signal)
            results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"Error in execute_trade_for_signals: {e}")
        return [f"Error: {str(e)}"]

# This function can be used for testing the module independently
async def main():
    test_signals = {'EURUSD': 'buy', 'GBPUSD': 'sell'}
    results = await execute_trade_for_signals(test_signals)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())