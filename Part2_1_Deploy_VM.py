# pip install azure-mgmt-resource azure-mgmt-network azure-mgmt-compute azure-identity python-dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from dotenv import load_dotenv
import os

# Loading environment variables from the .env file
load_dotenv()

# Fetching sensitive variables from the environment
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

# Initialize credentials and clients
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)

def create_virtual_network():
    """Create a Virtual Network (VNet) in the specified resource group."""
    print("Creating Virtual Network (VNet)...")
    vnet = network_client.virtual_networks.begin_create_or_update(
        resource_group,
        vnet_name,
        {
            "location": location,
            "address_space": {"address_prefixes": ["10.0.0.0/16"]}
        }
    ).result()
    return vnet


def create_network_security_group():
    """Create a Network Security Group (NSG)."""
    print("Creating Network Security Group...")
    nsg = network_client.network_security_groups.begin_create_or_update(
        resource_group,
        nsg_name,
        {
            "location": location
        }
    ).result()
    return nsg


def create_subnet(vnet, nsg):
    """Create a subnet and associate it with the NSG."""
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
    return subnet


def create_public_ip_address():
    """Create a Public IP Address."""
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
    return public_ip_address


def create_network_interface(subnet, public_ip_address):
    """Create a Network Interface (NIC) and associate it with the subnet and public IP address."""
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
    return nic


def create_virtual_machine(nic):
    """Create the virtual machine and associate it with the NIC."""
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
    vm_creation = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm_parameters).result()
    print(f"VM {vm_name} created successfully!")
    return vm_creation


def main():
    # Step 1: Create Virtual Network
    vnet = create_virtual_network()

    # Step 2: Create Network Security Group
    nsg = create_network_security_group()

    # Step 3: Create Subnet with NSG association
    subnet = create_subnet(vnet, nsg)

    # Step 4: Create Public IP Address
    public_ip_address = create_public_ip_address()

    # Step 5: Create Network Interface
    nic = create_network_interface(subnet, public_ip_address)

    # Step 6: Create Virtual Machine
    create_virtual_machine(nic)


if __name__ == '__main__':
    main()
