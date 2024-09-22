# pip install azure.mgmt.storage 
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage.models import VirtualNetworkRule, NetworkRuleSet


subscription_id = "aee8556f-d2fd-4efd-a6bd-f341a90fa76e"
resource_group_name  = "Data_Engineer"
storage_account_name = "dataengineerv1" 
vnet_name = "VNet-AtiehGharib" 
subnet_name = "Subnet-AtiehGharib"
vnet_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}"
print(f"VNet Resource ID: {vnet_resource_id}")


credential = DefaultAzureCredential()

# Initialize the Network Management Client
network_client = NetworkManagementClient(credential, subscription_id)

# Get the subnet properties
subnet = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)
# Check if service_endpoints is None, and initialize it if needed
if subnet.service_endpoints is None:
    subnet.service_endpoints = []

# Check if Microsoft.Storage service endpoint exists, and add it if not
if not any(se.service == 'Microsoft.Storage' for se in subnet.service_endpoints):
    subnet.service_endpoints.append({
        'service': 'Microsoft.Storage',
        'locations': ['westeurope']  # Adjust this based on your region
    })

    # Update the subnet with the new service endpoint
    network_client.subnets.begin_create_or_update(
        resource_group_name,
        vnet_name,
        subnet_name,
        subnet
    ).result()

# Initialize the Storage Management Client to update the storage account's networking settings
storage_client = StorageManagementClient(credential, subscription_id)

# Retrieve the current network rules for the storage account
storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)
network_rule_set = storage_account.network_rule_set

# If there are no network rules yet, initialize the network_rule_set
if not network_rule_set:
    network_rule_set = NetworkRuleSet(virtual_network_rules=[])

# Add the VNet and subnet to the network rules
vnet_rule = VirtualNetworkRule(
    virtual_network_resource_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}",
    action="Allow"
)

# Check if the VNet rule already exists to avoid duplicates
if vnet_rule not in network_rule_set.virtual_network_rules:
    network_rule_set.virtual_network_rules.append(vnet_rule)

    # Update the storage account with the new network rules
    storage_client.storage_accounts.update(
        resource_group_name,
        storage_account_name,
        {
            "network_rule_set": network_rule_set
        }
    )

    print(f"VNet {vnet_name} with subnet {subnet_name} added to the storage account {storage_account_name}'s networking settings.")
else:
    print(f"VNet {vnet_name} with subnet {subnet_name} is already added to the storage account {storage_account_name}'s networking settings.")