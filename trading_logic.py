from solana_utils import (
    get_network_congestion,
    get_token_price,
    should_sell_due_to_market_conditions,
)
from rugcheck_utils import check_token_safety

# Adaptive purchasing/selling
MIN_PURCHASE = 0.1 * 10**9  # 0.1 SOL in lamports
MAX_PURCHASE = 0.5 * 10**9  # 0.5 SOL in lamports
SLIPPAGE_TOLERANCE = 25  # in percentage
TARGET_RETURN = 20  # 20x return


def calculate_priority_fee(current_network_congestion):
    if current_network_congestion > 75:
        return 0.01 * 10**9
    return 0.001 * 10**9


def buy_token(token, amount_sol):
    if not check_token_safety(token):
        print(f"Token {token} failed safety check.")
        return
    priority_fee = calculate_priority_fee(get_network_congestion())
    slippage = amount_sol * (SLIPPAGE_TOLERANCE / 100)
    buy_amount = amount_sol + priority_fee
    if MIN_PURCHASE <= buy_amount <= MAX_PURCHASE:
        print(f"Attempting to buy {buy_amount/10**9} SOL worth of token {token}")
    else:
        print(f"Purchase amount {buy_amount/10**9} SOL out of specified range.")


def sell_token(token, initial_investment):
    current_price = get_token_price(token)
    target_price = initial_investment * TARGET_RETURN
    if current_price >= target_price:
        print(f"Selling token {token} at {current_price} for 20x return")
    elif should_sell_due_to_market_conditions(token):
        print(f"Emergency sell of token {token} at {current_price}")
