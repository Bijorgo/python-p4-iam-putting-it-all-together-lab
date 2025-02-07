#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        data = request.get_json()

        # Validate data
        if not data.get('username') or not data.get('password'):
            response = jsonify({"error": "Username and password are required"})
            return make_response(response, 422)

        # Create new instance
        try: 
            new_user = User(
                # Set attributes
                username=data['username'],
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
                # If problems with Null values or KeyError occurs, change these to
                # xxx=data.get('key', '')
                # this will prevent KeyError for nullable columns
            )
            # Use setter to has password
            new_user.password_hash = data['password']

            if User.query.filter_by(username=data['username']).first():
                response = jsonify({'error': 'Username already taken'})
                return make_response(response, 422)

            #if not new_user.username or not new_user.password_hash:
                #return jsonify({'error': 'Username and password are required'}), 422

            # Add and commit new instance to database
            db.session.add(new_user)
            db.session.commit()
        
            # Store user id in session to stay logged in
            session['user_id'] = new_user.id

            # Return JSON response
            response_data = {
                "id": new_user.id,
                "username": new_user.username,
                "image_url": new_user.image_url,
                "bio": new_user.bio
            }
            response = jsonify(response_data)
            return make_response(response, 201)  # Success
        
        # Integrty Error is raised by SQLAlchemy when a database constraint is violated
        # Here: if username is not unique 
        except IntegrityError:
            db.session.rollback()
            response = jsonify({"error": "Username already exists"})
            return make_response(response, 422)
        except Exception as exc:
            response = jsonify({"error": str(exc)})
            return make_response(response, 500)


class CheckSession(Resource):
    # Auto-login feature
    # GET request /check_session route
    # use get() method
    def get(self):
        # Check if the user is logged in by verifying if 'user_id' is in the session
        if 'user_id' in session:
            user_id = session['user_id']
            # Fetch the user details from the database using the user_id
            user = User.query.get(user_id)
            
            if user:  # User exists in the database
                response_data = {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
                response = jsonify(response_data)
                return make_response(response, 200)
            
            # User was found but is no longer valid (deleted, etc.)
            # session.pop('user_id', None)  # Remove invalid session data
            # response = jsonify({'error': 'User no longer exists'})
            # return make_response(response, 404)
            

        # If not logged in, return an error message with 401 status
        response = jsonify({'error': 'Unauthorized'})
        return make_response(response, 401)
    
# STOP, PASS TESTS BEFORE MOVING ON
# pytest testing/app_testing/app_test.py::TestCheckSession
# test in React App
    # log in, refresh, should still be logged in

class Login(Resource):
    def post(self):
        data = request.get_json()

        # Validate data
        if not data.get('username') or not data.get('password'):
            response = jsonify({"error": "Username and password are required"})
            return make_response(response, 422)
        
        # Check if the user exists in the database
        user = User.query.filter_by(username=data['username']).first()

        if user and user.authenticate(data['password']):
            # Store user id in session to stay logged in
            session['user_id'] = user.id

            # Return JSON response with user data
            response_data = {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
            response = jsonify(response_data)
            return make_response(response, 200)  # Success
        
        # If user doesn't exist or password is incorrect
        response = jsonify({"error": "Invalid username or password"})
        return make_response(response, 401)  # Unauthorized

# STOP. RUN TEST
# pytest testing/app_testing/app_test.py::TestLogin

class Logout(Resource):
    def delete(self):
        # If there is no active session (user_id not in session)
        if 'user_id' not in session or session['user_id'] is None:
            response = jsonify({'error': 'Unauthorized'})
            return make_response(response, 401)  # Return 401 Unauthorized if no active session

        # If user is logged in, remove 'user_id' from session
        session.pop('user_id', None)
        
        # Return an empty response with 204 (No Content) status
        return '', 204  # Success, no content




    # DELETE /logout route
    # delete() method
    # if user is logged in ( if user_id is in session object):
        # remove user id from session object
        # return empty response with status cose 204 (no content)
    # if user is not logged in
        # return JSON w error msg, status code 401 (unauthorized)
    
# STOP. TEST
# pytest testing/app_testing/app_test.py::TestLogout
# test in React App

class RecipeIndex(Resource):
    def get(self):
        # Retrieve the user ID from the session
        user_id = session.get('user_id')
        
        # If the user is not logged in, return a 401 Unauthorized response
        if not user_id:
            response = make_response({'error': 'Unauthorized'}, 401)
            return response

        # Fetch the user object from the database
        user = User.query.get(user_id)
        
        # If the user does not exist in the database, return a 404 Not Found error
        if not user:
            response = make_response({'error': 'User not found'}, 404)
            return response

        # Fetch all recipes associated with the logged-in user
        recipes = Recipe.query.filter_by(user_id=user.id).all()

        # Create a list of dictionaries with recipe details
        recipe_list = [
            {
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,  # Correct attribute name
            }
            for recipe in recipes
        ]

        # Return the list of recipes with a 200 status code
        response = make_response(recipe_list, 200)
        return response
    
    def post(self):
         # Retrieve the user ID from the session
        user_id = session.get('user_id')
        # If not logged in ... error
        if not user_id:
            return make_response({'error': 'Unauthorized'}, 401)

        # Get the JSON data from the request
        data = request.get_json()

        # Check for required fields
        if not data.get('title') or not data.get('instructions') or not data.get('minutes_to_complete'):
            return make_response({'error': 'Missing required fields'}, 400)

        # Fetch the user from the database
        user = User.query.get(user_id)

        if not user:
            return make_response({'error': 'User not found'}, 404)

        try:
            # Create the new recipe
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user.id
            )

            # Add the recipe to the session and commit
            db.session.add(recipe)
            db.session.commit()

        except ValueError as exe:
            # Catch the ValueError raised by the validates_instructions method
            #logging.error(f"Error creating recipe: {exe}")
            return make_response({'error': str(exe)}, 422)  # Return 422 error if validation fails

        # Return the created recipe with a 201 status code
        return make_response({
            'title': recipe.title,
            'instructions': recipe.instructions,
            'minutes_to_complete': recipe.minutes_to_complete
        }, 201)
    

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