import urllib
import http.client
import google.auth.transport.requests
import google.oauth2.id_token
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import requests

def make_authorized_get_request():
    """
    make_authorized_get_request makes a GET request to the specified HTTP endpoint
    by authenticating with the ID token obtained from the google-auth client library
    using the specified audience value.
    """

    # Cloud Run uses your service's hostname as the `audience` value
    # audience = 'https://timelime-backend-private-uavkhjofda-nw.a.run.app'
    # # For Cloud Run, `endpoint` is the URL (hostname + path) receiving the request
    endpoint = 'https://timelime-backend-private-uavkhjofda-nw.a.run.app/quentin'


    # auth_req = google.auth.transport.requests.Request()
    # id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    # print(id_token)

    # req = urllib.request.Request(endpoint)
    # req.add_header("Authorization", f"Bearer {id_token}")
    # # print(req.__dict__)
    # response = urllib.request.urlopen(req)
    # print(response.read())
    # return response.read()

    credentials = service_account.Credentials.from_service_account_file( 'secrets/timelime-dev-7f677154d05e.json',)
# Create a requests session with the authenticated credentials
    session = requests.Session()
    session.auth = credentials

    # Make the request to the Cloud Run service
    response = session.get(endpoint)
# Create an authorized session using the credentials
    # session = AuthorizedSession(credentials)

# Now you can use the session to make authenticated requests
    # response = session.get(endpoint)
    # print(response.content)


make_authorized_get_request()