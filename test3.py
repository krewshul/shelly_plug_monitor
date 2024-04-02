import os
from dotenv import dotenv_values, load_dotenv
import pymongo
import requests
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor


# Function to check for IP address variables in the .env file
def check_ip_addresses(env_file=".env"):
    # Load environment variables from the .env file
    env_vars = dotenv_values(env_file)

    # List to store found IP addresses
    ip_addresses = []

    # Check each variable for the IP_ADDRESS prefix
    for key, value in env_vars.items():
        if key.startswith("IP_ADDRESS"):
            ip_addresses.append(value)

    return ip_addresses

# Assuming MongoDB is running locally, handle connection errors
try:
    client = pymongo.MongoClient("mongodb://172.31.74.135:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Check the connection
except pymongo.errors.ConnectionFailure:
    print("Failed to connect to MongoDB, check if the MongoDB server is running")
    exit(5)

# Function to create MongoDB databases for each IP address
def create_mongo_databases(ip_addresses):
    for ip_address in ip_addresses:
        # Replace dots with underscores in the IP address for the database name
        ip_address_sanitized = ip_address.replace(".", "_")

        # Check if the database already exists
        if ip_address_sanitized not in client.list_database_names():
            # Create a new database for each sanitized IP address
            client[ip_address_sanitized]
            print(f"Created database: {ip_address_sanitized}")
        else:
            print(f"Database '{ip_address_sanitized}' already exists.")

# Function to make HTTP request and retrieve data for each IP address
def fetch_and_insert_switch_status(ip_address):
    # Get today's date
    today_date = datetime.now().strftime("%Y_%m_%d")
    ip_address_sanitized = ip_address.replace(".", "_")
    db_name = ip_address_sanitized
    collection_name = today_date

    # Prepare the document to be inserted; includes current Unix timestamp
    entry = {"timestamp": time.time()}  # Get current Unix timestamp

    try:
        # Construct the URL
        url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"
        # Make HTTP GET request
        response = requests.get(url, timeout=10)  # timeout added to avoid hanging

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Retrieve JSON data from the response and add it to the entry
            switch_status = response.json()
            entry.update(switch_status)  # Merge the switch status into the entry
        else:
            # Update the entry to indicate that data retrieval was unsuccessful
            entry.update({"status": "No Data Due To Error", "error_code": response.status_code})

        # Insert the entry into the MongoDB collection regardless of success or failure
        client[db_name][collection_name].insert_one(entry)
        if response.status_code == 200:
            print(f"Switch status data retrieved from {ip_address} and saved to MongoDB collection '{today_date}'.")
        else:
            print(f"Failed to retrieve switch status data from {ip_address}. Status code: {response.status_code}")

    except (requests.exceptions.RequestException, pymongo.errors.PyMongoError) as e:
        # Update the entry to indicate that an error occurred during the request
        entry.update({"status": "No Data Due To Error", "error_message": str(e)})
        # Insert the error entry into the MongoDB collection
        client[db_name][collection_name].insert_one(entry)
        print(f"An error occurred with {ip_address}: {e}")

if __name__ == "__main__":
    while True:
        ip_addresses = check_ip_addresses()
        if ip_addresses:
            print("IP addresses found in .env file:")
            for ip_address in ip_addresses:
                print(ip_address)
            create_mongo_databases(ip_addresses)
            
            # Create a ThreadPoolExecutor with a maximum of 5 threads
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit tasks for each IP address to the thread pool
                futures = [executor.submit(fetch_and_insert_switch_status, ip_address) for ip_address in ip_addresses]
                
                # Wait for all tasks to complete
                for future in futures:
                    future.result()  # This blocks until the future completes
        else:
            print("No IP addresses found in .env file.")

        # Wait for 10 seconds before repeating
        time.sleep(10)
