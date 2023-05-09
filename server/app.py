#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        json = request.get_json()
        # if json.get('username') and json.get('password'):
        user = User(
            username = json.get('username'),
            image_url = json.get('image_url'),
            bio = json.get('bio'),
        )
        user.password_hash = json['password']

        try:

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201
            
        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422
    pass

class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session['user_id']).first()

        if user:
            return user.to_dict(), 200
        
        return {}, 401
    pass

class Login(Resource):

    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()

        password = request.get_json().get('password')

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'errors': 'No user found'}, 401
    pass

class Logout(Resource):

    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        
        return {"error": "Unauthorized"}, 401
    pass

class RecipeIndex(Resource):

    def get(self):

        if session['user_id']:
            user = User.query.filter(User.id == session['user_id']).first()

            return [recipe.to_dict() for recipe in user.recipes], 200
        
        return {'error': "401 Unauthorized"}, 401

    def post(self):
        if session['user_id']:
            data = request.get_json()

            if len(data['instructions']) >= 50:

                new_recipe = Recipe(
                    title = data['title'],
                    instructions = data['instructions'],
                    minutes_to_complete = data['minutes_to_complete'],
                    user_id = session['user_id'],
                )

                db.session.add(new_recipe)
                db.session.commit()

                return new_recipe.to_dict(), 201

            return {'error': '422 Unprocessable Entity'}, 422
            
        return {'error': '401 Unauthorized'}, 401
        
        
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
