import json
import time
import random
from pathlib import Path
from web3 import Web3
from eth_account import Account

# === CONFIG ===
RPC = "https://rpc.minato.soneium.org"
CHAIN_ID = 1946
GAS_PRICE = Web3.to_wei(random.uniform(0.0045, 0.0055), "gwei")
GAS_LIMIT = 700000

WETH = "0x4200000000000000000000000000000000000006"
KYO = "0x9814A66E2bDdcfeB4E2D2290991C4C1D5411C800"
UNIVERSAL_ROUTER = "0x2B8825b95921769f4A8a14DaBa0C392216E73202"
POSITION_MANAGER = "0x0A9AfE979507Ea543aaacEAC88fFA1933F99b571"

# === INIT ===
w3 = Web3(Web3.HTTPProvider(RPC))
assert w3.is_connected(), "RPC not connected"

with open("wallet.txt") as f:
    PRIVATE_KEY = f.read().strip()
ACCOUNT = Account.from_key(PRIVATE_KEY)
WALLET = ACCOUNT.address

with open("abi.json") as f:
    abi_data = json.load(f)

weth = w3.eth.contract(address=WETH, abi=abi_data["WETH"])
kyo = w3.eth.contract(address=KYO, abi=abi_data["KYO"])
router = w3.eth.contract(address=UNIVERSAL_ROUTER, abi=abi_data["UniversalRouter"])
position = w3.eth.contract(address=POSITION_MANAGER, abi=abi_data["PositionManager"])

# === FUNCTIONS ===
def send_tx(to, data, value=0, max_retries=3):
    for attempt in range(max_retries):
        try:
            nonce = w3.eth.get_transaction_count(WALLET, "pending")
            tx = {
                "to": to,
                "from": WALLET,
                "value": value,
                "gas": GAS_LIMIT,
                "gasPrice": Web3.to_wei(random.uniform(0.0045, 0.0055), "gwei"),
                "nonce": nonce,
                "chainId": CHAIN_ID,
                "data": data
            }
            signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            return w3.to_hex(tx_hash)
        except ValueError as e:
            if "replacement transaction underpriced" in str(e):
                print(f"⚠️  Underpriced tx. Retrying... ({attempt+1}/{max_retries})")
                time.sleep(3)
            else:
                raise
    raise Exception("❌ Gagal mengirim transaksi setelah beberapa percobaan.")

def approve(token, spender, amount):
    data = token.functions.approve(spender, amount).build_transaction({"from": WALLET})["data"]
    tx = send_tx(token.address, data)
    print(f"[APPROVE] {token.address[:10]}... → {spender[:10]}...: {tx}")
    time.sleep(3)

def swap_weth_to_kyo(amount):
    approve(weth, UNIVERSAL_ROUTER, amount)
    path = [WETH, KYO]
    deadline = int(time.time()) + 60
    data = router.encodeABI("swapExactTokensForTokens", [amount, 0, path, WALLET, deadline])
    tx = send_tx(UNIVERSAL_ROUTER, data)
    print(f"[SWAP] {w3.from_wei(amount, 'ether')} WETH → KYO: {tx}")

def swap_kyo_to_weth(amount):
    approve(kyo, UNIVERSAL_ROUTER, amount)
    path = [KYO, WETH]
    deadline = int(time.time()) + 60
    data = router.encodeABI("swapExactTokensForTokens", [amount, 0, path, WALLET, deadline])
    tx = send_tx(UNIVERSAL_ROUTER, data)
    print(f"[SWAP] {w3.from_wei(amount, 'ether')} KYO → WETH: {tx}")

def add_liquidity(weth_amount, kyo_amount):
    approve(weth, POSITION_MANAGER, weth_amount)
    approve(kyo, POSITION_MANAGER, kyo_amount)

    params = {
        "token0": WETH,
        "token1": KYO,
        "fee": 3000,
        "tickLower": -887220,
        "tickUpper": 887220,
        "amount0Desired": weth_amount,
        "amount1Desired": kyo_amount,
        "amount0Min": 0,
        "amount1Min": 0,
        "recipient": WALLET,
        "deadline": int(time.time()) + 60
    }
    data = position.encodeABI("mint", [params])
    tx = send_tx(POSITION_MANAGER, data)
    print(f"[ADD LP] {w3.from_wei(weth_amount, 'ether')} WETH + {w3.from_wei(kyo_amount, 'ether')} KYO: {tx}")

def remove_liquidity_80_percent():
    # Periksa jumlah LP yang dimiliki
    lp_balance = position.functions.balanceOf(WALLET).call()
    if lp_balance == 0:
        print("⚠️ Tidak ada LP yang dapat di-remove.")
        return

    # Hitung 80% dari LP balance
    amount_to_remove = lp_balance * 80 // 100

    # Persiapkan data untuk transaksi remove liquidity
    params = {
        "tokenId": 0,  # Ganti dengan ID token LP jika diperlukan
        "liquidity": amount_to_remove,
        "amount0Min": 0,
        "amount1Min": 0,
        "deadline": int(time.time()) + 60
    }
    data = position.encodeABI("removeLiquidity", [params])
    tx = send_tx(POSITION_MANAGER, data)
    print(f"[REMOVE LP] Berhasil menghapus 80% LP: {tx}")

# === MAIN LOOP ===
if __name__ == "__main__":
    print("🚀 Auto swap & liquidity started!")

    while True:
        print("\n🌈 Starting new session of swaps...")
        total_weth_used = 0
        total_kyo_used = 0

        # 10x swap WETH → KYO
        for i in range(1, 11):
            amt = w3.to_wei(round(random.uniform(0.0001, 0.00015), 8), "ether")
            swap_weth_to_kyo(amt)
            total_weth_used += amt
            delay = random.randint(10, 30)
            print(f"⏱️ Waiting {delay} sec before next swap...")
            time.sleep(delay)

        # 10x swap KYO → WETH
        for i in range(1, 11):
            amt = w3.to_wei(round(random.uniform(0.0001, 0.00015), 8), "ether")
            swap_kyo_to_weth(amt)
            total_kyo_used += amt
            delay = random.randint(10, 30)
            print(f"⏱️ Waiting {delay} sec before next swap...")
            time.sleep(delay)

        print("✅ Finished swaps. Adding liquidity...")
        add_liquidity(total_weth_used, total_kyo_used)

        print("🛠️ Removing 80% of staked liquidity...")
        remove_liquidity_80_percent()

        next_sleep = random.randint(72000, 86400)  # 20–24 jam dalam detik
        hrs = round(next_sleep / 3600, 2)
        print(f"😴 Sleeping for {hrs} hours (~{next_sleep} seconds)...\n")
        time.sleep(next_sleep)
