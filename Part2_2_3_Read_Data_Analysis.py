# pip install azure-storage-blob pandas azure-identity python-dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Loading environment variables from the .env file
load_dotenv()

# Fetching sensitive data from the environment variables
storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
container_name_raw = os.getenv('CONTAINER_NAME_RAW')
blob_name_raw = os.getenv('BLOB_NAME_RAW')
container_name_upload = os.getenv('CONTAINER_NAME_UPLOAD')
directory_name = os.getenv('DIRECTORY_NAME')
blob_name_upload = f"{directory_name}/{os.getenv('BLOB_NAME_UPLOAD')}"
output_file_name = "Atieh-Gharib.csv"


def get_blob_service_client():
    """Create a BlobServiceClient using DefaultAzureCredential."""
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=credential
        )
        return blob_service_client
    except Exception as e:
        print(f"Error creating BlobServiceClient: {e}")
        raise


def download_blob_to_dataframe(blob_service_client, container_name, blob_name):
    """Download CSV from Azure Blob Storage and load it into a pandas DataFrame."""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Downloading the CSV data as text
        csv_data = blob_client.download_blob().content_as_text()

        # Converting the CSV text data into a Pandas DataFrame
        df = pd.read_csv(StringIO(csv_data))
        return df
    except Exception as e:
        print(f"Error downloading blob or converting to DataFrame: {e}")
        raise


def perform_data_analysis(df):
    """Perform data analysis on the DataFrame."""
    try:
        """Perform data analysis on the DataFrame."""
        # Group by 'country' and calculate the average 'Rating'
        # Equivalent SQL Query:
        # SELECT Country, AVG(Rating) AS avg_rate
        # FROM tourism_dataset
        # GROUP BY Country;

        average_rating_by_country = df.groupby('Country')['Rating'].mean().reset_index()
        average_rating_by_country = average_rating_by_country.rename(columns={'Rating': 'average_rating'})

        # Find the top 3 categories with the highest average 'Rating'
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

        return average_rating_by_country, top_3_categories
    except Exception as e:
        print(f"Error performing data analysis: {e}")
        raise


def plot_data(average_rating_by_country, top_3_categories):
    """Generate and save plots for the analysis results."""
    try:
        # a. Average Rating by Country
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 8))
        sns.barplot(x='average_rating', y='Country', data=average_rating_by_country, palette='viridis')
        plt.title('Average Rating by Country')
        plt.xlabel('Average Rating')
        plt.ylabel('Country')
        plt.tight_layout()
        plt.savefig('average_rating_by_country.png')
        print("Saved 'average_rating_by_country.png'.")
        plt.show()

        # b. Top 3 Categories with Highest Average Rating
        plt.figure(figsize=(8, 6))
        sns.barplot(x='average_rating', y='Category', data=top_3_categories, palette='magma')
        plt.title('Top 3 Categories with Highest Average Rating')
        plt.xlabel('Average Rating')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.savefig('top_3_categories.png')
        print("Saved 'top_3_categories.png'.")
        plt.show()
    except Exception as e:
        print(f"Error generating or saving plots: {e}")
        raise


def export_results_to_csv(average_rating_by_country, top_3_categories, output_file_name):
    """Export analysis results to a CSV file."""
    try:
        # Adding Multi-level Columns for better clarity
        average_rating_by_country.columns = pd.MultiIndex.from_product([['Avg rating by Country'], ['Country', 'average_rating']])
        top_3_categories.columns = pd.MultiIndex.from_product([['Top 3 Categories'], top_3_categories.columns])

        # Creating an empty DataFrame as a separator
        separator = pd.DataFrame(columns=pd.MultiIndex.from_product([[' '], [' ']]))

        combined_results = pd.concat([top_3_categories, separator, average_rating_by_country], axis=1)

        combined_results.to_csv(output_file_name, index=False, encoding='utf-8-sig')
        print(f"Aggregated results saved to {output_file_name}")
    except Exception as e:
        print(f"Error exporting results to CSV: {e}")
        raise


def upload_to_azure_storage(blob_service_client, container_name, blob_name, file_name):
    """Upload the CSV file to Azure Blob Storage."""
    try:
        container_client = blob_service_client.get_container_client(container_name)

        # Creating the container (directory) if it doesn't exist
        if not container_client.exists():
            container_client.create_container()

        # Uploading the CSV file to the container
        with open(file_name, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)

        print(f"File {file_name} uploaded to {directory_name} in container {container_name}.")
    except Exception as e:
        print(f"Error uploading file to Azure Storage: {e}")
        raise


def main():
    try:
        # Step 1: Getting Blob Service Client
        blob_service_client = get_blob_service_client()

        # Step 2: Downloading the CSV file into a DataFrame
        df = download_blob_to_dataframe(blob_service_client, container_name_raw, blob_name_raw)
        print(df.head())

        # Step 3: Performing Data Analysis
        average_rating_by_country, top_3_categories = perform_data_analysis(df)
        print("Average 'Rating' by country:\n", average_rating_by_country)
        print("\nTop 3 categories with the highest average 'Rating':\n", top_3_categories)

        # Step 4: Plotting the Data
        plot_data(average_rating_by_country, top_3_categories)

        # Step 5: Exporting results to CSV
        export_results_to_csv(average_rating_by_country, top_3_categories, output_file_name)

        # Step 6: Uploading results to Azure Blob Storage
        upload_to_azure_storage(blob_service_client, container_name_upload, blob_name_upload, output_file_name)

    except Exception as e:
        print(f"An error occurred during the execution of the main process: {e}")


if __name__ == '__main__':
    main()
