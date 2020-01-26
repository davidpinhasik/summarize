import os
from flask import g
from flask_oauthlib.client import OAuth

oauth = OAuth()

github = oauth.remote_app(
    'github', # name of app, can be anything
    consumer_key=os.getenv("GITHUB_CONSUMER_KEY"),  # standard param for all clients (FB, twitter, etc.)
    consumer_secret=os.getenv("GITHUB_CONSUMER_SECRET"),  # standard param for all clients (FB, twitter, etc.)
    request_token_params={"scope": "user:email"},  # params specific to client (github)
    base_url="https://api.github.com",
    request_token_url=None,  # this was used for oauth 1.0 but we are using 2.0 so this must be None
    access_token_method="POST",  # this is the second request, once user has authorised us, and specifies which
    # method to get the access_token from the api. For GitHub, this will be a POST request.
    access_token_url="https://github.com/login/oauth/access_token",  # this takes in the code client id and client secret
    authorize_url="https://github.com/login/oauth/authorize"  # this is where we send the user in that initial request
    # access_url, what we send the data to, so we can get back the access token. This url just takes in the client
    # id and state, etc.
)

@github.tokengetter
def get_github_token():
    if 'access_token' in g:
        return g.access_token
