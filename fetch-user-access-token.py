from google_auth_oauthlib.flow import InstalledAppFlow

# Set the scope for the access token (e.g., for Google Cloud Storage, use "https://www.googleapis.com/auth/devstorage.read_write")
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Set the path to your client secrets JSON file (downloaded from GCP Console)
CLIENT_SECRETS_FILE = 'secrets/oauth.json'

# Create the authentication flow
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

credentials = flow.run_local_server()

# Get the access token from the credentials
access_token = credentials.token
print("Access Token:", access_token)