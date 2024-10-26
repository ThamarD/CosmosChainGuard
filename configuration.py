# configuration.py by CosmosChainGuard version 0.8
# To check your node from a remote machine, you need to request RPC data.
# To be able to do this, you need to make the following changes in the config.toml file
# [rpc]
## # TCP or UNIX socket address for the RPC server to listen on
# original:
# laddr = "tcp://127.0.0.1:26657"
# ==> change into:
# laddr = "tcp://0.0.0.0:26657"
#
# Use '["*"]' to allow any origin
# cors_allowed_origins = []
# ==> change into:
# cors_allowed_origins = ["*"]
#
# Keep in mind: Node Configuration Changes - changes to config.toml increase the exposure of your node's RPC interface.
#   - Implement Security Measures: Use IP Whitelisting - Restrict access to specific IP addresses.
###############################################################################

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
CHAT_ID = 'your_chat_id'

# Timeout for requests (in seconds)
TIMEOUT_SECONDS = 3  # Adjust as needed

# Configuration for multiple Cosmos chains
COSMOS_CHAINS = [
    {
        'name': 'Your identifier',
        'node_url': 'http://your-node-ip:26657/status',
        'reference_node_url': 'https://reference-node/status',
        'backup_reference_node_url': 'https://backup-reference-node/status',
        'block_height_margin': 5,
        'min_peers': 5,
        'enabled': True,  # If True this chain will be checked
        'voting_power_change_threshold': 150  # Alerts for changes greater than 150
    },
    {
        'name': 'Your identifier',
        'node_url': 'http://your-node-ip:26657/status',
        'reference_node_url': 'https://reference-node/status',
        'backup_reference_node_url': 'https://backup-reference-node/status',
        'block_height_margin': 5,
        'min_peers': 5,
        'enabled': True,  # If True this chain will be checked
        'voting_power_change_threshold': 150  # Alerts for changes greater than 150
    }
    # Add more chains as needed
]

# Test mode flag
TEST_MODE = False  # Set this to False to disable test mode
