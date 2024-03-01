import os

import requests
from flask import Flask, jsonify, session, redirect, request

CAPITAL_ONE_API_KEY = 'your_api_key_here'
CAPITAL_ONE_ENDPOINT = 'https://api.capitalone.com/your_endpoint_here'


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used to secure session data

# Application's credentials and redirect URI
CLIENT_ID = os.environ.get('CAPITAL_ONE_CLIENT_ID')  # Get CLIENT_ID from environment variables
CLIENT_SECRET = os.environ.get('CAPITAL_ONE_CLIENT_SECRET')  # Get CLIENT_ID from environment variables
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'APPROPRIATE_SCOPE'
AUTHORIZATION_BASE_URL = 'https://api-sandbox.capitalone.com/oauth2/authorize'
TOKEN_URL = 'https://api-sandbox.capitalone.com/oauth2/token'


@app.route('/')
def home():
    # Generate a random state value for CSRF protection
    session['oauth_state'] = os.urandom(16).hex()
    # Redirect the user to the authorization URL
    auth_url = f'{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&state={session["oauth_state"]} '
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Validate state parameter for CSRF protection
    if request.args.get('state') != session.get('oauth_state'):
        return 'State value does not match. Potential CSRF attack.', 400

    # Capture the authorization code from the callback
    authorization_code = request.args.get('code')

    # Exchange the authorization code for an access token
    token_response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )
    token_data = token_response.json()
    session['access_token'] = token_data.get('access_token')

    # Redirect to a new page or display a message
    return 'You have successfully logged in.'


@app.route('/protected-resource')
def protected_resource():
    # Use the access token to access a protected resource
    if 'access_token' not in session:
        return 'You are not logged in.', 401

    headers = {
        'Authorization': f'Bearer {session["access_token"]}',
        'Content-Type': 'application/json'
    }

    # Example API request to Capital One
    response = requests.get('CAPITAL_ONE_PROTECTED_RESOURCE_ENDPOINT', headers=headers)
    return response.json()


@app.route('/account-info')
def get_account_info():
    headers = {'Authorization': 'Bearer YOUR_API_KEY'}
    response = requests.get('YOUR_API_ENDPOINT', headers=headers)
    if response.ok:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
