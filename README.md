# CosmosChainGuard

A simple stand-alone Python script to monitor Cosmos SDK-based blockchain nodes. The script checks the status of your nodes, compares them with reference nodes, and sends alerts via Telegram if any issues/updates are detected.

## Features

- Can monitor one or multiple Cosmos chains.
- Checks if your node(s) is/are syncing or behind in block height.
- Compares node block heights with (mulitple) reference nodes.
- Switches to backup reference nodes if primary reference node is syncing or behind.
- Monitors voting power changes and sends message if change is detected (amount threshold can be set)
- Checks the number of connected peers and sends message if under the set threshold.
- Sends alerts via Telegram.

## Prerequisites

- Python 3.7 or higher
- Access to the nodes you want to monitor
- A Telegram bot and chat ID for receiving alerts

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cosmos-node-monitor.git
cd cosmos-node-monitor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the Configuration File

Create a `configuration.py` file in the project directory using a text editor like `nano`:

```bash
nano configuration.py
```

**Example `configuration.py`:**

```python
# configuration.py

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
CHAT_ID = 'your_chat_id'

# Timeout for requests (in seconds)
TIMEOUT_SECONDS = 3  # Adjust as needed

# Configuration for multiple Cosmos chains
COSMOS_CHAINS = [
    {
        'name': 'ChainName-1',
        'node_url': 'http://your-node-ip:26657/status',
        'reference_node_url': 'https://reference-node/status',
        'backup_reference_node_url': 'https://backup-reference-node/status',
        'block_height_margin': 5,
        'min_peers': 5,
        'enabled': True,
        'voting_power_change_threshold': 200
    },
    {
        'name': 'ChainName-2',
        'node_url': 'http://your-node-ip:26657/status',
        'reference_node_url': 'https://reference-node/status',
        'backup_reference_node_url': 'https://backup-reference-node/status',
        'block_height_margin': 5,
        'min_peers': 5,
        'enabled': True,
        'voting_power_change_threshold': 10
    }
    # Add more chains as needed
]

# Test mode flag
TEST_MODE = False
```

**Important:** Do not share your `TELEGRAM_BOT_TOKEN` and `CHAT_ID` publicly.

### 4. Adjust Node Configuration (Optional)

If you're running the script on the same machine as your Cosmos node no changes needed if you only want to check this node.
If you want to monitor more nodes on different machines, you may need to adjust your node's configuration to allow external access to the RPC endpoints.

To allow the script to access your node's RPC endpoints, you need to adjust your node's configuration (`config.toml`).

**Note:** Be cautious when exposing your node's RPC endpoints. Exposing RPC endpoints can pose security risks.

- **Enable External Access to RPC:**
  - In `app.toml`, set the `laddr` parameter under `[rpc]`:

    ```toml
    [rpc]
    laddr = "tcp://0.0.0.0:26657"
    ```

- **Allow Cross-Origin Requests:**
  - Set `cors_allowed_origins` to allow requests from any origin:

    ```toml
    cors_allowed_origins = ["*"]
    ```

- **Security Recommendations:**
  - **Restrict Access:** Use firewall rules to restrict access to trusted IP addresses, via uwf or your Cloud service provider.

## Usage

### Updating the Configuration

- Update the `COSMOS_CHAINS` list in `configuration.py` with your chain details.
- Ensure all URLs are correct and accessible.

## Running the Script

Execute the script using Python:

```bash
python3 monitor.py
```

You can also set up a cron job or a systemd service to run the script at regular intervals.

## Logging

The script uses Python's `logging` module to log information. By default, it logs messages to the console at the `INFO` level.

To change the logging level, modify the `basicConfig` call in `monitor.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Security Considerations

- **Protect Sensitive Data:**
  - Do not share sensitive information like Telegram tokens or chat IDs publicly.
  - Be cautious when storing sensitive data in configuration files.

- **Node Security:**
  - Be cautious when exposing RPC endpoints.
  - Restrict access using firewalls and access control lists.
  - Enable authentication and use secure communication protocols if supported.


## Future Features

- **Asynchronous Execution for Multiple Chains:**
  - Implementing asynchronous HTTP requests to monitor multiple chains concurrently, improving performance and efficiency.

- **Additional Enhancements:**
  - Improved error handling and resilience.
  - Enhanced configuration management.
  - Integration with other notification channels (e.g., email, Slack).
  - Web-based dashboard for real-time monitoring.


To run the script every 15 minutes using cron, you can create a crontab entry that schedules the execution of your Python script at the desired interval.

## Setting Up the Cron Job

Here are the steps to schedule your `monitor.py` script to run every 15 minutes:

### Edit the Crontab File

Open the crontab editor for your user:

```bash
crontab -e
```

If it's your first time using `crontab`, it might ask you to select an editor. Choose your preferred text editor (e.g., nano).

### 3. Add the Cron Job Entry

Add the following line to the crontab file.
Always use absolute paths in cron jobs to avoid issues with the working directory:

```cron
*/15 * * * * /usr/bin/python3 /home/youruser/cosmos_monitor/monitor.py >> /home/youruser/cosmos_monitor/monitor.log 2>&1
```


## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bugs.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [Cosmos SDK](https://github.com/cosmos/cosmos-sdk)
- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Requests Library](https://github.com/psf/requests)
