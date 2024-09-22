#!/bin/bash

# SSH into the VM 
ssh myusername@51.144.94.14 

# Step 1: Installing Azure CLI on VM
echo "Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Step 2: Checking Azure CLI installation
az --version

# Step 3: Checking the network rules for the storage account
az storage account show -n dataengineerv1 --query networkRuleSet

# Step 4: Getting the network interface ID for the VM
NIC_ID=\$(az vm show --resource-group Data_Engineer --name VM-AtiehGharib --query networkProfile.networkInterfaces[0].id -o tsv)

# Step 5: Getting the subnet ID for the network interface
SUBNET_ID=\$(az network nic show --ids \$NIC_ID --query "ipConfigurations[0].subnet.id" -o tsv)

# Step 6: Adding network rule for the storage account 
echo "Adding network rule for VNet..."
az storage account network-rule add --resource-group Data_Engineer --account-name dataengineerv1 --vnet-name VNet-AtiehGharib --subnet Subnet-AtiehGharib

# Step 7: Listing blobs in the storage container
echo "Listing blobs in the storage container..."
az storage blob list \
  --account-name dataengineerv1 \
  --container-name atieh-gharib \
  --account-key " " \
  --output table

# Step 8: Downloading the CSV file to the home directory (i.e. VM)
echo "Downloading CSV file to home directory..."
az storage blob download \
  --account-name dataengineerv1 \
  --container-name atieh-gharib \
  --name Atieh-Gharib/Atieh-Gharib.csv \
  --file ~/result-Atieh.csv \
  --account-key " "

# Step 9: Checking if the file was downloaded successfully
echo "Checking downloaded file..."
ls ~
cat ~/result-Atieh.csv


