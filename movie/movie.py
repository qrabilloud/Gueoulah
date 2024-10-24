from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response

import resolvers as r

PORT = 3001
HOST = '0.0.0.0'
app = Flask(__name__)

# Create elements for Ariadne
type_defs = load_schema_from_path('movie.graphql')
query = QueryType()
query.set_field('all_movies', r.all_movies)
query.set_field('movie_with_id', r.movie_with_id)
query.set_field('all_actors', r.all_actors)
query.set_field('actor_with_id', r.actor_with_id)

movie = ObjectType('Movie')
movie.set_field('actors', r.resolve_actors_in_movie)

actor = ObjectType('Actor')
actor.set_field('films', r.resolve_movies_in_actor)

mutation = MutationType()
mutation.set_field('update_movie_rate', r.update_movie_rate)
mutation.set_field('create_movie', r.create_movie)
mutation.set_field('delete_movie', r.delete_movie)
mutation.set_field('create_actor', r.create_actor)
mutation.set_field('delete_actor', r.delete_actor)
mutation.set_field('add_actor_movie', r.add_actor_movie)
mutation.set_field('delete_actor_movie', r.delete_actor_movie)
schema = make_executable_schema(type_defs, movie, query, mutation, actor)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=None, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)