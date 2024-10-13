import logging
from metaapi_integration import metaapi_client  # Replace with the correct import

def execute_trade(symbol, action, volume):
    """Executes a trade with the given parameters."""
    try:
        trade_response = metaapi_client.execute_trade(
            symbol=symbol,
            action=action,
            volume=volume,
        )
        logging.info(f"Trade executed: {trade_response}")
        return trade_response
    except Exception as e:
        logging.error(f"Trade execution failed: {e}")
        return None

if __name__ == '__main__':
    # Example parameters
    symbol = 'EURUSD'  # Trading pair
    action = 'buy'     # Action: 'buy' or 'sell'
    volume = 1.0      # Volume of the trade

    # Execute the trade
    trade_result = execute_trade(symbol, action, volume)
    print(trade_result)  # Print the result
