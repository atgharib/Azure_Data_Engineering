from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.models import VirtualNetwork, Subnet, NetworkInterface, PublicIPAddress
from azure.mgmt.compute.models import VirtualMachine, HardwareProfile, StorageProfile, OSDisk, ImageReference, OSProfile, NetworkInterfaceReference, NetworkProfile
from dotenv import load_dotenv
import os

# Loading environment variables from .env file
load_dotenv()

# Fetching sensitive variables from environment
subscription_id = os.getenv('SUBSCRIPTION_ID')
resource_group = os.getenv('RESOURCE_GROUP')
location = os.getenv('LOCATION')
vm_name = os.getenv('VM_NAME')
vnet_name = os.getenv('VNET_NAME')
subnet_name = os.getenv('SUBNET_NAME')
nic_name = os.getenv('NIC_NAME')
ip_name = os.getenv('IP_NAME')
nsg_name = os.getenv('NSG_NAME')
vm_size = os.getenv('VM_SIZE')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')


credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)


print("Creating Virtual Network (VNet)...")
vnet = network_client.virtual_networks.begin_create_or_update(
    resource_group,
    vnet_name,
    {
        "location": location,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]}
    }
).result()

print("Creating Network Security Group...")
nsg = network_client.network_security_groups.begin_create_or_update(
    resource_group,
    nsg_name,
    {
        "location": location
    }
).result()


print("Creating Subnet within the VNet with NSG association...")
subnet = network_client.subnets.begin_create_or_update(
    resource_group,
    vnet_name,
    subnet_name,
    {
        "address_prefix": "10.0.0.0/24",
        "network_security_group": {
            "id": nsg.id
        }
    }
).result()


print("Creating Public IP Address...")
public_ip_address = network_client.public_ip_addresses.begin_create_or_update(
    resource_group,
    ip_name,
    {
        "location": location,
        "sku": {"name": "Basic"},
        "public_ip_allocation_method": "Dynamic"
    }
).result()


print("Creating Network Interface (NIC)...")
nic = network_client.network_interfaces.begin_create_or_update(
    resource_group,
    nic_name,
    {
        "location": location,
        "ip_configurations": [{
            "name": "IPConfig1",
            "subnet": {"id": subnet.id},
            "public_ip_address": {"id": public_ip_address.id}
        }]
    }
).result()


print("Creating Virtual Machine...")
vm_parameters = {
    "location": location,
    "hardware_profile": {"vm_size": vm_size},
    "storage_profile": {
        "image_reference": {
            "publisher": "Canonical",
            "offer": "0001-com-ubuntu-server-jammy", 
            "sku": "22_04-lts-gen2",  
            "version": "latest"
        },
        "os_disk": {
            "name": f"{vm_name}-osdisk",
            "caching": "ReadWrite",
            "create_option": "FromImage",
            "managed_disk": {"storage_account_type": "Standard_LRS"}
        }
    },
    "os_profile": {
        "computer_name": vm_name,
        "admin_username": username,
        "admin_password": password
    },
    "network_profile": {
        "network_interfaces": [{"id": nic.id}]
    }
}

if __name__=='__main__':
    vm_creation = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm_parameters).result()
    print(f"VM {vm_name} created successfully!")
