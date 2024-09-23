# Azure Data Engineering Assignment

This repository contains the solutions and code implementation for an Azure Data Engineering assignment. The project demonstrates key concepts of working with Azure services, including Azure Storage, and Virtual Machines.

## Author
Atieh Gharib

## Overview
The project includes Python scripts that leverage Azure SDKs and services to:
- Deploy Azure resources such as Virtual Machines and Networking components.
- Ingest and analyze data stored in Azure Blob Storage.
- Perform data processing and aggregation using Pandas.
- Visualize the processed data using Seaborn and Matplotlib.
- Export and upload results back to Azure Blob Storage.

## Contents
- **Python Scripts**: The repository contains Python scripts for various Azure Data Engineering tasks, such as deploying infrastructure, processing data, and managing storage.
- **Environment Configuration**: The `.env` file is used to manage sensitive configuration details securely.
- **Data Analysis**: Scripts for processing data, generating plots, and storing results.
- **Bash Script**: A bash script to automate downloading CSV files from Azure Blob Storage to your VM.

## Requirements
To run the scripts, you will need:
- Python 3.x
- Azure SDK for Python
- Pandas, Matplotlib, Seaborn
- Azure CLI 

## Instructions
1. Clone the repository.
2. Install the necessary dependencies:
   pip install -r requirements.txt
   
4. Update the `.env` file with your Azure credentials and configuration.
5. Run the individual Python scripts as needed to perform specific tasks.
5. To download the resulting CSV file from Azure Blob Storage to the home directory of your VM, you can run:  
bash part2_4_SSH_DownloadToVM.sh  
or  
chmod +x part2_4_SSH_DownloadToVM.sh


