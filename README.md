#### Cisco XDR_AUTOMATE Automation Relay Module

This Python-based application serves as a bridge between Cisco XDR Automation workflows and various functionalities within the XDR platform, including dashboard tile creation, data enrichment, and sightings management.

## Overview

The Cisco XDR Integration Module aims to streamline the process of integrating XDR workflows with the XDR platform, enhancing visibility and automation capabilities for security analysts and administrators. By leveraging this application, users can easily translate XDR workflows into actionable insights and enriched data within XDR.

## Features

1. **Dashboard Tile Creation**: Automatically generate dashboard tiles based on the output of XDR workflows, enabling users to visualize key security metrics and indicators at a glance.

2. **Enrichment**: Enrich security events and indicators with additional contextual information sourced from XDR workflows, enhancing the depth of analysis and improving decision-making.

3. **Sightings Management**: Facilitate the management of security sightings within the XDR platform, allowing for efficient tracking, investigation, and response to potential threats.

## Requirements

- Python 3.x
- Cisco XDR Tenant
- Required Python packages (specified in `requirements.txt`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/brebouch/tr-05-xdr-automation-relay.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the deployment script to deploy the serverless app and configure the integration:

```bash
python deploy_relay.py deploy -r <AWS region> -p <Project name> -x <XDR Automate Region> -i <XDR Automate API Client ID> -s <XDR Automate API Client Secret> -m <Memory for Serverless Instance> -t <Relay Timeout in Seconds>
```

4. Import Create XDR Relay Module Instance.json workflow in XDR Automation

## Usage

1. Run the XDR Relay Module Instance workflow providing details for all input values

2. Update the newly deployed integration with the Deliberation workflow to provide judgement lookups
3. Update the newly deployed integration with the Observe workflow to provide sighting events


## Contribution
Contributions are welcome! If you encounter any issues, have suggestions for improvements, or would like to add new features, please feel free to open an issue or submit a pull request.

## License
MIT License

## Disclaimer
This application is provided as-is without any warranty. Use at your own risk. The developers and contributors are not liable for any damages or losses arising from the use of this software.
