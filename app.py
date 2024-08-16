import hashlib
import os
import time
import requests
import threading
import random

def print_welcome_message():
    """Prints the welcome message."""
    print('KatKoin')

coins = 0

def get_public_ip():
    """Fetches the public IP address of the machine."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Check for request errors
        ip_address = response.json().get('ip')
        return ip_address
    except requests.RequestException as e:
        print(f"Error fetching IP: {e}")
        return None

def generate_wallet_key(length=32, algorithm='sha256'):
    """Generates a wallet key using the specified hashing algorithm."""
    random_bytes = os.urandom(length)
    hash_object = hashlib.new(algorithm, random_bytes)
    return hash_object.hexdigest()

def read_keys_from_file(filename='keys.txt'):
    """Reads the keys from a file and returns a dictionary of wallet keys to (IP, balance)."""
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as file:
        lines = file.readlines()
    keys = {}
    for line in lines:
        parts = line.strip().split(' ', 2)
        if len(parts) == 3:
            ip, key, balance = parts
            keys[key] = {'ip': ip, 'balance': int(balance)}
    return keys

def write_keys_to_file(keys, filename='keys.txt'):
    """Writes the dictionary of wallet keys to a file."""
    with open(filename, 'w') as file:
        for key, data in keys.items():
            file.write(f"{data['ip']} {key} {data['balance']}\n")

def get_balance(wallet_key):
    """Gets the balance for a specific wallet key."""
    keys = read_keys_from_file()
    return keys.get(wallet_key, {}).get('balance', 0)

def set_balance(wallet_key, balance):
    """Sets the balance for a specific wallet key."""
    keys = read_keys_from_file()
    if wallet_key in keys:
        keys[wallet_key]['balance'] = balance
        write_keys_to_file(keys)

def send_coins(amount, sender_key, receiver_key):
    """Send coins from one wallet to another."""
    global coins
    keys = read_keys_from_file()

    if sender_key not in keys:
        print('Sender wallet key not found.')
        return
    if receiver_key not in keys:
        print('Receiver wallet key not found.')
        return

    sender_balance = keys[sender_key]['balance']
    if amount > sender_balance:
        print('Insufficient coins to send.')
        return

    # Deduct from sender and add to receiver
    set_balance(sender_key, sender_balance - amount)
    receiver_balance = keys[receiver_key]['balance']
    set_balance(receiver_key, receiver_balance + amount)
    print(f'Sent {amount} KatKoin from {sender_key} to {receiver_key}.')

def start_mining(wallet_key):
    """Starts mining coins for a specific wallet key."""
    if not wallet_key:
        print("Invalid wallet key.")
        return
    
    print(f"Started mining for wallet key: {wallet_key}")
    while True:
        time.sleep(10)
        keys = read_keys_from_file()
        if wallet_key in keys:
            current_balance = keys[wallet_key]['balance']
            new_balance = current_balance + 1
            set_balance(wallet_key, new_balance)
            print(f"Updated balance for {wallet_key}: {new_balance} KatKoin")
        else:
            print("Wallet key not found.")
            break

def commands():
    mining_thread = None
    
    while True:
        user_input = input('Type in commands here: ').strip().lower()

        if user_input == 'test':
            print('test')
        elif user_input == 'wallet -show key':
            public_ip = get_public_ip()
            if not public_ip:
                print('Unable to fetch IP address, please try again later.')
                time.sleep(1.5)
                continue

            # Load existing keys
            keys = read_keys_from_file()

            # Reverse lookup to get the wallet key
            wallet_key = next((key for key, data in keys.items() if data['ip'] == public_ip), None)
            if wallet_key:
                print(f'Existing Wallet Key for IP {public_ip}: {wallet_key}')
            else:
                new_key = generate_wallet_key()
                keys[new_key] = {'ip': public_ip, 'balance': coins}
                write_keys_to_file(keys)
                print(f'Generated Wallet Key for IP {public_ip}: {new_key}')
        elif user_input == 'exit':
            print('Exiting...')
            time.sleep(1.5)
            break
        elif user_input == 'wallet -show':
            public_ip = get_public_ip()
            keys = read_keys_from_file()
            wallet_key = next((key for key, data in keys.items() if data['ip'] == public_ip), None)
            if wallet_key:
                print(f'Your current balance is: {keys[wallet_key]["balance"]} KatKoin')
            else:
                print('No wallet key found for the current IP address.')
        elif user_input == 'wallet -send':
            print(f'How much KatKoin do you want to send?')
            amount_str = input('How much KatKoin do you want to send? ').strip()
            if not amount_str.isdigit():
                print('Must be a number!')
                continue

            amount = int(amount_str)
            if amount <= 0:
                print('Amount must be greater than zero!')
                continue

            sender_key = input('Enter your wallet key: ').strip()
            receiver_key = input('Enter the recipient\'s wallet key: ').strip()
            are_you_sure1 = input(f'Do you want to send {amount} KatKoin from {sender_key} to {receiver_key}? (yes/no) ').strip().lower()
            if are_you_sure1 == 'yes':
                send_coins(amount, sender_key, receiver_key)
                print('Transaction completed.')
            else:
                print('Transaction cancelled.')
        elif user_input == 'start -mine':
            wallet_key = input('Enter your wallet key: ').strip()
            if mining_thread and mining_thread.is_alive():
                print("Mining is already in progress.")
            else:
                mining_thread = threading.Thread(target=start_mining, args=(wallet_key,))
                mining_thread.start()
        else:
            print('Unknown command.')

def main():
    print_welcome_message()
    commands()

if __name__ == "__main__":
    main()
