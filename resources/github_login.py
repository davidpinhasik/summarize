from flask import g, request, url_for
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from oa import github

from models.user import UserModel

class GithubLogin(Resource):
    @classmethod
    def get(cls):
        """
        In order to begin the authorization flow, we need to send to GitHub that we want to authorize. We do that by
        sending the user over to the GitHub Authorization page, along with our details. Then, GitHub will see those
        details and send the user over to the login page (or to their "Do you want to authorize this app" page). All
        we have to do here is to send the user to GitHub with our details, and the github client that we created can
        do that with the github.authorize() method. It takes a callback, which is the important point here and states
        where do we want to go once the user has been authorized. This will be the url that we originally put in to our
        GitHub OAuth app on their site.
        """
        #  return github.authorize(callback="http://localhost:5000/login/github/authorized")
        return github.authorize(url_for("github.authorize", external=True))  # github.authorize is name of endpoint.
        # external=True means that we want to build a full url and not just for internal use. For example, internal
        # would be /login/github/authorized and external would be http://localhost:5000/login/github/authorized.
        # And the github.authorize is the name of the endpoint that is defined in the add_resource() in app.py for the
        # GithubAuthorize resource.


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        resp = github.authorized_response()  # this gives us access to resp['access_token'] by making the POST
        # response for us

        if resp is None or resp.get("access_token") is None:
            error_response = {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }
            return error_response

        g.access_token = resp['access_token']  # this gives us access_token, but no user info.
        github_user = github.get('user')  # This will get the user's information from the github client
        print(f"github_user.data = {github_user.data}")
        github_username = github_user.data['login']  # the username of how they logged in to github

        user = UserModel.find_by_username(github_username)

        if not user:
            user = UserModel(username=github_username, password=None, email=None, soc_security_num=None)
            user.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}, 200




