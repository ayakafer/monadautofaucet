import requests
from twocaptcha import TwoCaptcha
import random
import time
import sys
import itertools
from eth_account import Account

LOGO_TEXT = "FER Monad Bot"
CREDITS = "by Developer"

def display_logo():
    logo = """
███████╗███████╗██████╗ 
██╔════╝██╔════╝██╔══██╗
█████╗  █████╗  ██████╔╝
██╔══╝  ██╔══╝  ██╔══██╗
██║     █████║  ██║  ██║
╚═╝     ╚═╝     ╚═╝  ╚═╝
    """
    for char in logo:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.002)
    print("\n")
    print("Script by: github.com/ayakafer\n")

def generate_wallet():
    acct = Account.create()
    return acct.address, acct.key.hex()

def save_wallet(address, private_key, filename="wallets.txt"):
    with open(filename, "a") as file:
        file.write(f"Address: {address}\nPrivate Key: {private_key}\n\n")

def load_proxies(filename="proxy.txt"):
    try:
        with open(filename, "r") as file:
            proxies = [line.strip() for line in file.readlines() if line.strip()]
        return proxies
    except FileNotFoundError:
        print("File proxy.txt tidak ditemukan! Pastikan file tersebut ada.")
        return []

display_logo()
use_proxy = input("Gunakan proxy? (y/n): ").strip().lower()
proxy_list = load_proxies() if use_proxy == "y" else []
num_claims = int(input("Masukkan jumlah klaim yang diinginkan: "))

print("Pilih layanan anti-captcha:")
print("1. 2Captcha")
print("2. Anti-Captcha")
captcha_choice = input("Masukkan pilihan (1/2): ").strip()
api_key = input("Masukkan API key untuk layanan captcha: ").strip()

def solve_captcha(image_url):
    response = requests.get(image_url)
    with open("captcha.png", "wb") as f:
        f.write(response.content)
    
    if captcha_choice == "1":
        solver = TwoCaptcha(api_key)
    elif captcha_choice == "2":
        from anticaptchaofficial.imagecaptcha import imagecaptcha
        solver = imagecaptcha()
        solver.set_key(api_key)
    else:
        print("Pilihan tidak valid.")
        return None
    
    return solver.normal("captcha.png") if captcha_choice == "1" else solver.solve_and_return_solution("captcha.png")

FAUCET_URL = "https://testnet.monad.xyz/api/auth/session"

for i in range(num_claims):
    ev_address, private_key = generate_wallet()
    save_wallet(ev_address, private_key)
    print(f"[{i+1}/{num_claims}] Generated EVM Address: {ev_address}")
    
    proxy_config = None
    if proxy_list:
        current_proxy = proxy_list[i % len(proxy_list)]  # Pilih proxy secara bergiliran
        proxy_config = {"http": current_proxy, "https": current_proxy}
    
    captcha_image_url = "https://testnet.monad.xyz/captcha"
    captcha_code = solve_captcha(captcha_image_url) if captcha_choice in ["1", "2"] else None
    
    headers = {"Content-Type": "application/json"}
    data = {"address": ev_address}
    if captcha_code:
        data["captcha"] = captcha_code
    
    response = requests.post(FAUCET_URL, json=data, headers=headers, proxies=proxy_config)
    
    if response.status_code == 200:
        print(f"✅ [{i+1}/{num_claims}] Berhasil klaim faucet Monad Testnet!")
        print("Respon:", response.json())
    else:
        print(f"❌ [{i+1}/{num_claims}] Gagal klaim faucet.")
        print("Kode status:", response.status_code)
        print("Respon:", response.text)
