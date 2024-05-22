from dotenv import load_dotenv
import requests
import os

MAUTIC_BASE_URL = os.getenv('MAUTIC_BASE_URL')
MAUTIC_CLIENT_ID = os.getenv('MAUTIC_CLIENT_ID')
MAUTIC_CLIENT_SECRET = os.getenv('MAUTIC_CLIENT_SECRET')
# Set up the Mautic API client


def create_user(data):
    try:
        payload =  {
            "firstname": data["first_name"],
            "lastname": data["last_name"],
            "email": data["email"],
            "company_name": data["com_name"],
            "company_vat": data["com_vat"],
            "company_street": data["com_street"],
            "company_street_number": data["com_street_number"],
            "company_postal_code": data["com_postal"],
            "company_city": data["com_city"],
            "company_country": data["com_country"],
            "company_website_url": data["com_website"],
            "language": "en",
            "aiana_status": "registered",
            "bots_active": 0,
            "aiana_environment": "TEST",
            "license": "FREE",
            "person_source":"APPLICATION",
        }

        create_user_url = f'{MAUTIC_BASE_URL}/contacts/new'
        print(create_user_url)

        access_token = get_access_token()
        # Headers including the access token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        # Sending the POST request
        response = requests.post(create_user_url, data=payload, headers=headers)
        print(response)
        # Checking response
        if response.status_code == 201:
            print("User created successfully")
            return response.json()  # or handle as needed
        else:
            print("Failed to create user", response.text)
            return None
    except Exception as e:
        print(e)

def get_access_token():
    token_url = f'{MAUTIC_BASE_URL}/oauth/v2/token'
    data = {
        'client_id': '1_2iy2ky40kr8ko48g0008k4osggwcg880s4ow8c8s4ogg888kw8',
        'client_secret': '4cll695h3b8kscskgccc44ogg40s8cgcgosoo4wgc84k04ksok',
        'grant_type':'client_credentials'
    }

    response = requests.post(token_url, data)

    # Checking if the request was successful
    if response.status_code == 200:
        # If the response is successful, parse it as JSON
        response_data = response.json()  # This converts the JSON response to a Python dictionary
        print("Response Data:", response_data)
        # Example of accessing specific data in the response
        access_token = response_data.get('access_token')  # Assuming the token is returned in 'access_token'
        print("Access Token:", access_token)
        return access_token
    else:
        # If the response was not successful, print the status code and response text
        print("Failed to retrieve data")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print(response.data)
        return resonse.status_code


