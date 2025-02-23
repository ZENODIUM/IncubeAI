import requests

# Replace with your IBM API key
API_KEY = ""

# IBM IAM token endpoint
IAM_URL = "https://iam.cloud.ibm.com/identity/token"

# Headers for the token request
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

# Data payload for the token request
data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": API_KEY
}

# Make the POST request to get the access token
response = requests.post(IAM_URL, headers=headers, data=data)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response to get the access token
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print(f"Failed to get access token. Status code: {response.status_code}")
    print("Response:", response.text)