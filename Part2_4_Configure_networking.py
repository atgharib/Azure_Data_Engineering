from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage.models import VirtualNetworkRule, NetworkRuleSet
from dotenv import load_dotenv
import os

load_dotenv()

subscription_id = os.getenv('SUBSCRIPTION_ID')
resource_group_name = os.getenv('RESOURCE_GROUP')
storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
vnet_name = os.getenv('VNET_NAME')
subnet_name = os.getenv('SUBNET_NAME')
location = os.getenv('LOCATION')

vnet_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}"
print(f"VNet Resource ID: {vnet_resource_id}")

credential = DefaultAzureCredential()

def get_subnet(network_client):
    """Retrieve and update the subnet with the Microsoft.Storage service endpoint."""
    # Getting the subnet properties
    subnet = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)

   
    if subnet.service_endpoints is None:
        subnet.service_endpoints = []

    # Adding the Microsoft.Storage service endpoint if it doesn't exist
    if not any(se.service == 'Microsoft.Storage' for se in subnet.service_endpoints):
        subnet.service_endpoints.append({
            'service': 'Microsoft.Storage',
            'locations': [location] 
        })

        # Updating the subnet with the new service endpoint
        network_client.subnets.begin_create_or_update(
            resource_group_name,
            vnet_name,
            subnet_name,
            subnet
        ).result()
        print(f"Microsoft.Storage endpoint added to the subnet {subnet_name}")
    else:
        print(f"Microsoft.Storage endpoint already exists in subnet {subnet_name}")

    return subnet


def update_storage_network_rules(storage_client, subnet):
    """Update the storage account with the new virtual network rules."""
    # Retrieving the current network rules for the storage account
    storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)
    network_rule_set = storage_account.network_rule_set

   
    if not network_rule_set:
        network_rule_set = NetworkRuleSet(virtual_network_rules=[])

   
    vnet_rule = VirtualNetworkRule(
        virtual_network_resource_id=subnet.id,
        action="Allow"
    )

    # Checking if the VNet rule already exists to avoid duplicates
    if vnet_rule not in network_rule_set.virtual_network_rules:
        network_rule_set.virtual_network_rules.append(vnet_rule)

        # Updating the storage account with the new network rules
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


def main():
    """Main function to update subnet and storage account network rules."""
    # Initializing Network Management Client
    network_client = NetworkManagementClient(credential, subscription_id)

    # Step 1: Getting and updating subnet with Microsoft.Storage endpoint
    subnet = get_subnet(network_client)

    # Initializing Storage Management Client
    storage_client = StorageManagementClient(credential, subscription_id)

    # Step 2: Updating storage account's network rules
    update_storage_network_rules(storage_client, subnet)


if __name__ == '__main__':
    main()
