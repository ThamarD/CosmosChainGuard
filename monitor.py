# CosmosChainGuard version 0.8 (with modifications)
import requests
import asyncio
from telegram import Bot
import logging
import configuration
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import configuration from configuration.py
TELEGRAM_BOT_TOKEN = configuration.TELEGRAM_BOT_TOKEN
CHAT_ID = configuration.CHAT_ID
COSMOS_CHAINS = configuration.COSMOS_CHAINS
TEST_MODE = configuration.TEST_MODE
TIMEOUT_SECONDS = configuration.TIMEOUT_SECONDS


bot = Bot(token=TELEGRAM_BOT_TOKEN)

# File to store the previous voting power
VOTING_POWER_FILE = 'voting_power.json'


def load_previous_voting_power():
    if os.path.exists(VOTING_POWER_FILE):
        try:
            with open(VOTING_POWER_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in {VOTING_POWER_FILE}: {e}")
            # Optionally, you can delete the corrupted file or initialize it
            return {}
    return {}


def save_previous_voting_power(voting_power_data):
    try:
        with open(VOTING_POWER_FILE, 'w') as f:
            json.dump(voting_power_data, f)
        logging.debug(f"Saved voting power data: {voting_power_data}")
    except (TypeError, ValueError) as e:
        logging.error(f"Error saving voting power data: {e}")


def check_node_status(chain, previous_voting_power, messages):
    try:
        # Get the response from your node
        response = requests.get(chain['node_url'], timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'sync_info' in data['result']:
                # Extract the current block height from your node
                current_block_height = int(data['result']['sync_info']['latest_block_height'])
                is_syncing = data['result']['sync_info']['catching_up']

                # Check if your node is syncing
                if is_syncing:
                    messages.append(f"Warning: {chain['name']} node is syncing!")
                    logging.warning(f"{chain['name']} node is syncing!")

                # Get the response from the reference node, passing your node's block height and messages
                ref_response = get_reference_node_response(chain, current_block_height, messages, timeout=TIMEOUT_SECONDS)

                if ref_response and ref_response.status_code == 200:
                    ref_data = ref_response.json()
                    if 'result' in ref_data and 'sync_info' in ref_data['result']:
                        # Extract the block height from the reference node
                        reference_block_height = int(ref_data['result']['sync_info']['latest_block_height'])

                        # Calculate the block height difference
                        block_height_difference = abs(current_block_height - reference_block_height)

                        # Check if the block height difference exceeds the margin
                        if block_height_difference > chain['block_height_margin']:
                            messages.append(
                                f"Warning: Block height difference is too large for {chain['name']}! "
                                f"(My node: {current_block_height}, Reference node: {reference_block_height}, difference: {block_height_difference} )"
                            )
                            logging.warning(
                                f"Block height difference is too large for {chain['name']}! "
                                f"(My node: {current_block_height}, Reference node: {reference_block_height})"
                            )
                        else:
                            logging.info(
                                f"{chain['name']} block height is within the margin. "
                                f"(My node: {current_block_height}, Reference node: {reference_block_height})"
                            )
                    else:
                        messages.append(f"Error: Invalid response from the reference node API for {chain['name']}.")
                        logging.error(f"Invalid response from the reference node API for {chain['name']}.")
                else:
                    messages.append(
                        f"Error: Reference node API returned status code "
                        f"{ref_response.status_code if ref_response else 'N/A'} for {chain['name']}."
                    )
                    logging.error(
                        f"Reference node API returned status code "
                        f"{ref_response.status_code if ref_response else 'N/A'} for {chain['name']}."
                    )

                # Check voting power
                if 'validator_info' in data['result']:
                    validator_info = data['result']['validator_info']
                    current_voting_power = int(validator_info['voting_power'])
                    previous_voting_power_chain = previous_voting_power.get(chain['name'], current_voting_power)

                    voting_power_change = abs(current_voting_power - previous_voting_power_chain)
                    logging.info(f"{chain['name']} current voting power: {current_voting_power}")

                    if voting_power_change >= chain['voting_power_change_threshold']:
                        messages.append(
                            f"Info: Voting power change for {chain['name']}! "
                            f"New voting power: {current_voting_power}, "
                            f"a change of: {current_voting_power - previous_voting_power_chain}"
                        )
                        logging.warning(
                            f"Voting power change detected for {chain['name']}: "
                            f"New voting power: {current_voting_power}, "
                            f"Previous voting power: {previous_voting_power_chain}, "
                            f"Change: {voting_power_change}"
                        )

                    # Update the previous voting power for the next check
                    previous_voting_power[chain['name']] = current_voting_power
                else:
                    logging.error(f"Validator info not found in the response for {chain['name']}.")

                # Check number of peers
                check_node_health(chain, messages)
            else:
                messages.append(f"Error: Invalid response from the node API for {chain['name']}.")
                logging.error(f"Invalid response from the node API for {chain['name']}.")
        else:
            messages.append(f"Error: Node API returned status code {response.status_code} for {chain['name']}.")
            logging.error(f"Node API returned status code {response.status_code} for {chain['name']}.")
    except requests.Timeout:
        messages.append(f"Error: Request timed out when connecting to the node API for {chain['name']}.")
        logging.error(f"Request timed out when connecting to the node API for {chain['name']}.")
    except requests.RequestException as e:
        messages.append(f"Error: Cannot connect to the node API for {chain['name']}.")
        logging.error(f"Cannot connect to the node API for {chain['name']}. Exception: {e}")

def get_reference_node_response(chain, my_node_block_height, messages, timeout=TIMEOUT_SECONDS):
    try:
        ref_response = requests.get(chain['reference_node_url'], timeout=timeout)
        if ref_response.status_code == 200:
            ref_data = ref_response.json()
            is_syncing = ref_data['result']['sync_info']['catching_up']
            ref_block_height = int(ref_data['result']['sync_info']['latest_block_height'])
            if is_syncing or ref_block_height < my_node_block_height:
                logging.warning(
                    f"Primary reference node for {chain['name']} is syncing or behind, switching to backup node."
                )
                return get_backup_reference_node_response(chain, my_node_block_height, messages, timeout)
            return ref_response
        else:
            logging.warning(
                f"Primary reference node for {chain['name']} returned status code {ref_response.status_code}, switching to backup node."
            )
            return get_backup_reference_node_response(chain, my_node_block_height, messages, timeout)
    except requests.Timeout:
        logging.warning(
            f"Request timed out when connecting to the primary reference node for {chain['name']}, switching to backup node."
        )
        return get_backup_reference_node_response(chain, my_node_block_height, messages, timeout)
    except requests.RequestException as e:
        logging.warning(
            f"Primary reference node for {chain['name']} is not available ({e}), switching to backup node."
        )
        return get_backup_reference_node_response(chain, my_node_block_height, messages, timeout)

def get_backup_reference_node_response(chain, my_node_block_height, messages, timeout=TIMEOUT_SECONDS):
    try:
        backup_ref_response = requests.get(chain['backup_reference_node_url'], timeout=timeout)
        if backup_ref_response.status_code == 200:
            backup_ref_data = backup_ref_response.json()
            is_syncing = backup_ref_data['result']['sync_info']['catching_up']
            backup_ref_block_height = int(backup_ref_data['result']['sync_info']['latest_block_height'])
            if is_syncing or backup_ref_block_height < my_node_block_height:
                logging.error(
                    f"Backup reference node for {chain['name']} is also syncing or behind."
                )
                messages.append(
                    f"Error: Both the primary and backup reference nodes for {chain['name']} are syncing or behind."
                )
                return None
            return backup_ref_response
        else:
            logging.error(
                f"Backup reference node for {chain['name']} returned status code {backup_ref_response.status_code}."
            )
            messages.append(
                f"Error: Cannot connect to both the primary and backup reference nodes for {chain['name']}."
            )
            return None
    except requests.Timeout:
        logging.error(
            f"Request timed out when connecting to the backup reference node for {chain['name']}."
        )
        messages.append(
            f"Error: Request timed out when connecting to both the primary and backup reference nodes for {chain['name']}."
        )
        return None
    except requests.RequestException as e:
        logging.error(
            f"Backup reference node for {chain['name']} is also not available: {e}"
        )
        messages.append(
            f"Error: Cannot connect to both the primary and backup reference nodes for {chain['name']}."
        )
        return None

def check_node_health(chain, messages):
    try:
        net_info_url = chain['node_url'].replace('status', 'net_info')
        net_info_response = requests.get(net_info_url, timeout=TIMEOUT_SECONDS)
        if net_info_response.status_code == 200:
            net_info_data = net_info_response.json()
            peers = net_info_data['result']['peers']

            if len(peers) < chain['min_peers']:
                messages.append(
                    f"Warning: The number of peers is too low for {chain['name']}! "
                    f"(Current number of peers: {len(peers)}, Minimum number of peers: {chain['min_peers']})"
                )
                logging.warning(
                    f"Warning: The number of peers is too low for {chain['name']}! "
                    f"(Current number of peers: {len(peers)}, Minimum number of peers: {chain['min_peers']})"
                )
            else:
                logging.info(
                    f"The number of peers for {chain['name']} is sufficient. "
                    f"(Current number of peers: {len(peers)}, Minimum number of peers: {chain['min_peers']})"
                )
        else:
            messages.append(
                f"Error: Cannot get peers information from the node API for {chain['name']}. "
                f"Status code: {net_info_response.status_code}"
            )
            logging.error(
                f"Error: Cannot get peers information from the node API for {chain['name']}. "
                f"Status code: {net_info_response.status_code}"
            )
    except requests.Timeout:
        messages.append(f"Error: Request timed out when connecting to the net_info API for {chain['name']}.")
        logging.error(f"Request timed out when connecting to the net_info API for {chain['name']}.")
    except requests.RequestException as e:
        messages.append(f"Error: Cannot connect to the net_info API for {chain['name']}.")
        logging.error(f"Cannot connect to the net_info API for {chain['name']}. {e}")

def send_telegram_message(message):
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message))

def main():
    previous_voting_power = load_previous_voting_power()
    logging.debug(f"Loaded previous voting power data: {previous_voting_power}")
    messages = []
    for chain in COSMOS_CHAINS:
        if chain.get('enabled', True):
            check_node_status(chain, previous_voting_power, messages)
    save_previous_voting_power(previous_voting_power)
    if messages:
        send_telegram_message('\n'.join(messages))

if __name__ == "__main__":
    main()
