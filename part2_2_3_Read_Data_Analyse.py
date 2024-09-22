# pip install azure-storage-blob pandas azure-identity python-dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Fetch sensitive data from the environment variables
storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
container_name_raw = os.getenv('CONTAINER_NAME_RAW')
blob_name_raw = os.getenv('BLOB_NAME_RAW')
container_name_upload = os.getenv('CONTAINER_NAME_UPLOAD')
directory_name = os.getenv('DIRECTORY_NAME')
blob_name_upload = f"{directory_name}/{os.getenv('BLOB_NAME_UPLOAD')}"
password = os.getenv('PASSWORD')

'''Step 2: Read Data from Azure Storage Account'''

# Creating a BlobServiceClient using DefaultAzureCredential
credential = DefaultAzureCredential()

# Constructing the Blob Service Client URL
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=credential
)

# Getting the container client
container_client = blob_service_client.get_container_client(container_name_raw)

# Getting the blob client for the specific CSV file
blob_client = container_client.get_blob_client(blob_name_raw)

# Downloading the CSV data as text
csv_data = blob_client.download_blob().content_as_text()

# Converting the CSV text data into a Pandas DataFrame
df = pd.read_csv(StringIO(csv_data))

print(df.head())

'''Step 3: Perform Data Analysis'''

# 1. Group the data by the 'country' column and calculate the average value of the "Rate" column.
# Equivalent SQL Query:
# SELECT Country, AVG(Rating) AS avg_rate
# FROM tourism_dataset
# GROUP BY Country;

average_rating_by_country = df.groupby('Country')['Rating'].mean().reset_index()
average_rating_by_country = average_rating_by_country.rename(columns={'Rating': 'average_rating'})
print("Average 'Rating' by country:")
print(average_rating_by_country)

# 2. Find the top 3 categories with the highest average rate across all countries.
# Equivalent SQL Query:
# SELECT Category, AVG(Rating) AS avg_rate
# FROM tourism_dataset
# GROUP BY Category
# ORDER BY avg_rate DESC
# LIMIT 3;

average_rating_by_category = df.groupby('Category')['Rating'].mean().reset_index()
average_rating_by_category = average_rating_by_category.rename(columns={'Rating': 'average_rating'})
average_rating_by_category = average_rating_by_category.sort_values(by='average_rating', ascending=False)
top_3_categories = average_rating_by_category.head(3)

print("\nTop 3 categories with the highest average 'Rating':")
print(top_3_categories)

'''Step 4: Export Results and Save to VM'''

# Save both average_rating_by_country and average_rating_by_category to a CSV file
output_file_name = "Atieh-Gharib.csv"

# Adding Multi-level Columns (for better clarity)
average_rating_by_country.columns = pd.MultiIndex.from_product([['Avg rating by Country'], ['Country', 'average_rating']])
top_3_categories.columns = pd.MultiIndex.from_product([['top 3 categories'], top_3_categories.columns])

# Creating an empty DataFrame to act as the separator
separator = pd.DataFrame(columns=pd.MultiIndex.from_product([[' '], [' ']]))

combined_results = pd.concat([top_3_categories, separator, average_rating_by_country], axis=1)

combined_results.to_csv(output_file_name, index=False, encoding='utf-8-sig')

print(f"Aggregated results saved to {output_file_name}")

'''Upload to Azure Storage'''

# Create BlobServiceClient to interact with the Azure Blob Storage
container_client = blob_service_client.get_container_client(container_name_upload)

# Create the container (directory) if it doesn't exist
if not container_client.exists():
    container_client.create_container()

# Upload the CSV file to the container
with open(output_file_name, "rb") as data:
    container_client.upload_blob(name=blob_name_upload, data=data, overwrite=True)

print(f"File {output_file_name} uploaded to {directory_name} in container {container_name_upload}.")
