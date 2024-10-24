# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import super_pb2

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def isUserExisting(userid):
   for user in users:
      if user['id'] == userid:
         return True
   return False

def write(users):
    with open('{}/data/users.json'.format("."), 'w') as f:
        json.dump({"users" : users}, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_all_users() -> str:
    """Return all the users in the database"""
    return make_response(jsonify(users), 200)

@app.route("/users", methods = ['POST'])
def create_user() -> str:
   """Create en user using the content of the http request"""
   user = request.get_json()
   if isUserExisting(user['id']) : return make_response("This user is already existing", 409)
   users.append(user)
   write(users)
   return make_response(user, 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid : str) -> str:
   """Searches all the users in the database with a specific id."""
   for user in users:
         if str(user['id']) == str(userid):
            return make_response(jsonify(user), 200) 
   return make_response("No user with this id.", 400)

@app.route("/users/<userid>", methods=['PUT'])
def update_user(userid : str) -> str:
   if not isUserExisting(userid) : return make_response("Unexisting user", 400)
   req = request.get_json()
   if req['id'] != userid and isUserExisting(req['id']): return make_response("Id already used by another user", 409)
   for user in users:
      if user['id'] == userid:
         user['id'] = req['id']
         user['name'] = req['name']
         user['last_active'] = req['last_active']
   write(users)
   return make_response(user, 200)


@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid : str) -> str:
   """Delete the user with id userid"""
   global users
   newUsers = []
   deletedUsers = []
   for user in users:
         if user['id'] != userid:
            newUsers.append(user)
         else :
            deletedUsers.append(user)
   users = newUsers
   write(newUsers)
   return make_response(jsonify(deletedUsers), 200)

@app.route("/users/name", methods=['GET'])
def get_users_byname() -> str:
   """Searches all the users in the database with a specific name."""
   username = request.get_data(as_text=True)
   usersWithName = [user for user in users if user['name'].lower() == username.lower()]
   return make_response(jsonify(usersWithName), 200)

def makeResponseMovie(respMovie, function, messageNoData = None):
   """Create the response for Rest using the result of the GraphQL request"""
   if respMovie.status_code != 200 : return make_response(respMovie.content, 500)
   respJson = respMovie.json()
   if 'errors' in respJson: return make_response(respJson['errors'][0]['message'], 400)
   res = respJson['data'][function]
   if res == None : return make_response(messageNoData if messageNoData else "", 400 if messageNoData else 200)
   return make_response(res, 200)

@app.route("/movies", methods=['GET'])
def get_all_movies() -> str:
   """Get all the movies in the database"""
   reqMovie = {"query": "query {all_movies {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}"}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json=reqMovie)
   return makeResponseMovie(respMovie, "all_movies")

@app.route("/movies/<id>", methods=['GET'])
def get_movie_byId(id : str) -> str:
   """Get the movie having this id"""
   reqMovie = {"query": "query ($_id:String!) {movie_with_id(_id: $_id) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_id":id}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json=reqMovie)
   return makeResponseMovie(respMovie, "movie_with_id", "Unknow id")

@app.route("/movies", methods=['POST'])
def create_movie() -> str:
   """Create a movie using the body of the request"""
   req = request.get_json()
   reqMovie = {"query": "mutation ($_id:String!, $_title:String!, $_director:String!, $_rate:Float!, $_actors:[String]!) {create_movie(_id: $_id, _title: $_title, _director: $_director, _rate: $_rate, _actors: $_actors) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_id": req['id'], "_title": req['title'], "_director": req['director'], "_rate": req['rating'], "_actors": req['actors']}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, 'create_movie')
   

@app.route("/movies/<id>", methods=['DELETE'])
def delete_movie(id: str) -> str:
   """Delete a movie (using his id)"""
   reqMovie = {"query": "mutation ($_id:String!) {delete_movie(_id: $_id) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_id":id}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "delete_movie")

@app.route("/actors", methods=['GET'])
def get_all_actors() -> str:
   """Get all the actors in the database"""
   reqMovie = {"query": "query {all_actors {id, firstname, lastname, birthyear, films{id, title, director, rating}}}"}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "all_actors")

@app.route("/actors/<id>", methods=['GET'])
def get_actor_with_id(id : str) -> str:
   """Get the actor having this id"""
   reqMovie = {"query": "query ($_id:String!) {actor_with_id(_id: $_id) {id, firstname, lastname, birthyear, films{id, title, director, rating}}}",
               "variables": {"_id":id}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "actor_with_id", "Unknow id")

@app.route("/actors", methods=['POST'])
def create_actor() -> str:
   """Create an actor using the body of the request"""
   req = request.get_json()
   reqMovie = {"query": "mutation ($_id:String!, $_firstname:String!, $_lastname:String!, $_birthyear:Int!, $_films:[String]!) {create_actor(_id: $_id, _firstname: $_firstname, _lastname: $_lastname, _birthyear: $_birthyear, _films: $_films) {id, firstname, lastname, birthyear, films{id, title, director, rating}}}",
               "variables": {"_id": req['id'], "_firstname": req['firstname'], "_lastname": req['lastname'], "_birthyear": req['birthyear'], "_films": req['films']}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "create_actor")

@app.route("/actors/<id>", methods=['DELETE'])
def delete_actor(id: str) -> str:
   """Delete an actor (using his id)"""
   reqMovie = {"query": "mutation ($_id:String!) {delete_actor(_id: $_id) {id, firstname, lastname, birthyear, films{id, title, director, rating}}}",
               "variables": {"_id":id}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "delete_actor")

@app.route("/movies/<idMovie>/<idActor>", methods=['PUT'])
def add_actor_movie(idMovie: str, idActor: str) -> str:
   """Add an actor to a movie (and the movie to the actor)"""
   reqMovie = {"query": "mutation ($_idMovie:String!, $_idActor:String!) {add_actor_movie(_idMovie: $_idMovie, _idActor: $_idActor) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_idMovie": idMovie, "_idActor": idActor}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "add_actor_movie")

@app.route("/movies/<idMovie>/<idActor>", methods=['DELETE'])
def delete_actor_movie(idMovie: str, idActor: str) -> str:
   """Delete an actor in a movie (and the movie in the actor)"""
   reqMovie = {"query": "mutation ($_idMovie:String!, $_idActor:String!) {delete_actor_movie(_idMovie: $_idMovie, _idActor: $_idActor) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_idMovie": idMovie, "_idActor": idActor}}
   respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
   return makeResponseMovie(respMovie, "delete_actor_movie")

@app.route("/actors/<idActor>/<idMovie>", methods=['PUT'])
def add_movie_actor(idActor : str, idMovie : str) -> str:
   """Add a movie to an actor (and the actor to the movie)"""
   return add_actor_movie(idMovie, idActor)

@app.route("/actors/<idActor>/<idMovie>", methods=['DELETE'])
def delete_movie_actor(idActor: str, idMovie: str) -> str:
   """Delete a movie in an actor (and the actor in the movie)"""
   return delete_actor_movie(idMovie, idActor)

def getObjFromListAttr(list, attr, val):
   """Get the object in the list list having it's attribute attr equal to val. Return None otherwise"""
   for l in list:
      if l[attr] == val:
         return l
   return None

def groupByUser(bookings):
   """Group the bookings (where the user is precised in each booking) by users"""
   groupedBookings = []
   for booking in bookings:
      user = getObjFromListAttr(groupedBookings, 'userid', booking['userid'])
      if not user:
         user = {'userid' : booking['userid'], 'bookings' : []}
         groupedBookings.append(user)
      user['bookings'].append({'date' : booking['date'], 'movies' : booking['movies']})
   return groupedBookings

@app.route("/users/<userid>/bookings", methods = ['GET'])
def get_booking_user(userid : str) -> str:
   """Searches all the bookings of an user in the database"""
   with grpc.insecure_channel('localhost:3003') as channel:
      stub = booking_pb2_grpc.BookingStub(channel)
      print(stub)
      print("-------------- GetBookingByUser --------------")
      bookings = stub.GetBookingsByUser(booking_pb2.UserID(userid=userid)).bookings
   channel.close()
   convertedBookings = [{'userid' : booking.userid, 'date' : booking.date.date, 'movies' : list(booking.date.movies) } for booking in bookings]
   if not convertedBookings : return make_response({'dates' : []}, 200)
   userBookings = groupByUser(convertedBookings)[0]['bookings']
   return make_response(jsonify({'dates' : userBookings}), 200)

@app.route("/users/<userid>/bookings/details", methods = ['GET'])
def get_detailed_booking_user(userid : str) -> str:
   """Searches all the bookings of an user in the database, and show all the details for each movie"""
   if not isUserExisting(userid) : return make_response("Unexisting user", 400)
   with grpc.insecure_channel('localhost:3003') as channel:
      stub = booking_pb2_grpc.BookingStub(channel)
      print(stub)
      print("-------------- GetBookingByUser --------------")
      bookings = stub.GetBookingsByUser(booking_pb2.UserID(userid=userid)).bookings
   channel.close()
   convertedBookings = [{'userid' : booking.userid, 'date' : booking.date.date, 'movies' : list(booking.date.movies) } for booking in bookings]
   if not convertedBookings : return make_response({'bookings' : []}, 200)
   userBookings = groupByUser(convertedBookings)[0]['bookings']
   books = {'dates' : userBookings}
   #Here we got the bookings of the user, now we got the data of the movies
   for date in books['dates']:
      detailedMovies = []
      for movie in date['movies']:
         reqMovie = {"query": "query ($_id:String!) {movie_with_id(_id: $_id) {id, title, director, rating, actors{firstname, lastname, birthyear, id}}}",
               "variables": {"_id":movie}}
         respMovie = requests.post("http://127.0.0.1:3001/graphql", json = reqMovie)
         if respMovie.status_code != 200 : return make_response("An issue occured when retrieving a movie data : " + respMovie.content, 500)
         respJson = respMovie.json()
         if 'errors' in respJson : return make_response(respJson, 400)
         detailedMovies.append(respJson['data']['movie_with_id'])
      date['movies'] = detailedMovies
   return make_response(books, 200)

@app.route("/users/<userid>/book", methods = ['POST', 'DELETE'])
def create_or_delete_booking_for_user(userid : str) -> str:
   """Create or delete a booking for the user userid"""
   req = request.get_json()
   if not isUserExisting(userid) : return make_response("Unexisting user", 409)
   if request.method == 'POST':
      with grpc.insecure_channel('localhost:3003') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         print("-------------- AddBookingByUser --------------")
         stub.AddBookingByUser(booking_pb2.BookingData(userid=userid, date=super_pb2.TimeShow(date=req['date'], movies=[req['movie']])))
      channel.close()
   else:
      with grpc.insecure_channel('localhost:3003') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         print("-------------- DeleteBookingByUser --------------")
         stub.DeleteBookingByUser(booking_pb2.BookingData(userid=userid, date=super_pb2.TimeShow(date=req['date'], movies=[req['movie']])))
      channel.close()
   return get_booking_user(userid)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
