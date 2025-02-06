#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        return "Not done here yet, just want the squiggles gone"
    # create POST /signup route
    # if the user is valid:
        # save new user to db with username, encrypted pw, img url, bio
        # save users id in session object as user_id
        #return a JSON response with the users ID, username, img url, and bio, and status code 201 (created)
    # if not valid:
        #return JSON response with error message, status code 422 (Unprocessable Entity)
        # Error message may need to be able to deal with multiple types of errors due to validations in models

class CheckSession(Resource):
    pass
    # Auto-login feature
    # GET request /check_session route
    # use get() method
        # if user is logged in (if user_id is in the session object):
            #return JSON response with user's ID, username, img url, bio, status code 200 (sucess)
        # if not logged in:
            # return JSON response with error message, status code 401 (unauthorized)
# STOP, PASS TESTS BEFORE MOVING ON
# pytest testing/app_testing/app_test.py::TestCheckSession
# test in React App
    # log in, refresh, should still be logged in

class Login(Resource):
    pass
    # PPOST /login route
    # post() method
    # if user and pw authenticated:
        # save users id in session object
        # return JSON resonse w user ID, username, img url, bio
    # if user / pw not authenticated:
        # return JSON response w error msg, status code 401 (unauthorized)

# STOP. RUN TEST
# pytest testing/app_testing/app_test.py::TestLogin

class Logout(Resource):
    pass
    # DELETE /logout route
    # delete() method
    # if user is loggef in ( if user_id is in session object):
        # remove user id from session object
        # return empty response with status cose 204 (no content)
    # if user is not logged in
        # return JSON w error msg, status code 401 (unauthorized)
    
# STOP. TEST
# pytest testing/app_testing/app_test.py::TestLogout
# test in React App

class RecipeIndex(Resource):
    pass
    # GET /recipes route
    # get() method
    # if logged in:
        # return JSON response w array of all recipes w title, instructions, minutes to complete, along w nested user object, status code 200 (sucess)
    # if not logged in:
        # return JSON response w error mgs, status code 401 (unauthorized)

    # POST /recipes route
    # post() method
    # if logged in:
        # save new recipe to db if its valid
            # recipe should belong to logged in user
            # should have title, instructions, and minutes procided from request JSON
        # return JSON response w title, instructionss, minutes, nested user obj, status code 201 (created)
    # if not logged in:
        # return JSON response w error, 401 (unauthorized)
    # if recipe is not valid:
        #return JSON response w error messages, code 422 (unprocessable Entitle)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)