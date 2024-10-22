import json
import time

from graphql import GraphQLError


def writeAsJson(filePath, data):
    """Write the data as a json in the file at the path filePath"""
    with open(filePath.format("."), "w") as wfile:
        json.dump(data, wfile)

def writeMovies(movies):
    """Write movies in the database Movies"""
    return writeAsJson('{}/data/movies.json', movies)

def writeActors(actors):
    """Write actors in the database Actors"""
    return writeAsJson('{}/data/actors.json', actors)

def readAsJson(filePath):
    """Read the file filePath as a json"""
    with open(filePath.format("."), "r") as rfile:
        jsonData = json.load(rfile)
        return jsonData

def readMovies():
    """Read the database Movies"""
    return readAsJson('{}/data/movies.json')

def readActors():
    """Read the database Actors"""
    return readAsJson('{}/data/actors.json')

movies = readMovies()
actors = readActors()

def getObjFromListAttr(list, attr, val):
   """Get the object in the list list having it's attribute attr equal to val. Return None otherwise"""
   for l in list:
      if l[attr] == val:
         return l
   return None

def getListActors(actorsIds, actors = actors['actors'], raiseError = False):
    """Get the list of all the actors in actors having their id in actorsIds. Raise an error if raiseError = True and an id is not found in actors"""
    actorsList = []
    for id in actorsIds:
        actor = getObjFromListAttr(actors, 'id', id)
        if not actor:
            if raiseError: raise GraphQLError('Actor not found ' + id)
        else:
            actorsList.append(actor)
    return actorsList

def resolve_actors_in_movie(movie, info):
    """Resolve the actors list in a movie"""
    return getListActors(movie['actors'])

def getListMovies(moviesIds, movies = movies['movies'], raiseError = False):
    """Get the list of all the movies in movies having their id in moviesIds. Raise an error if raiseError = True and an id is not found in movies"""
    moviesList = []
    for id in moviesIds:
        movie = getObjFromListAttr(movies, 'id', id)
        if not movie:
            if raiseError: raise GraphQLError('Movie not found ' + id)
        else :
            moviesList.append(movie)
    return moviesList

def resolve_movies_in_actor(actor, info):
    """Resolve the films list in an actor"""
    return getListMovies(actor['films'])

#Used for testing and debuging. No entry point for this function
def syncActorMovie():
    '''Sync actor['films'] -> movie['actor'] if needed'''
    for actor in actors['actors']:
        for actMovie in actor['films']:
            movieActor = getObjFromListAttr(movies['movies'], 'id', actMovie)
            if movieActor :
                if not (actor['id'] in movieActor['actors']):
                    movieActor['actors'].append(actor['id'])
    writeMovies(movies)

def movie_with_id(_,info,_id):
    """Get the movie having the id _id"""
    return getObjFromListAttr(movies['movies'], 'id', _id)

def all_movies(_, info):
    """Get all the movies"""
    return movies['movies']

def update_movie_rate(_,info,_id,_rate):
    """Update the rate of the movie _id"""
    movie = getObjFromListAttr(movies['movies'], 'id', _id)
    if not movie : raise GraphQLError('Unexisting movie ' + _id)
    movie['rating'] = _rate
    writeMovies(movies)
    return movie

def create_movie(_, info, _id, _title, _director, _rate, _actors):
    """Create a movie using the parameters"""
    movie = {"title": _title, "id": _id, "rating": _rate, "director":_director, "actors":_actors}
    if getObjFromListAttr(movies['movies'], 'id', _id): raise GraphQLError('id already used')
    actorsPlaying = getListActors(_actors, actors['actors'], True)
    for actor in actorsPlaying:
        actor['films'].append(_id)
    movies['movies'].append(movie)
    writeMovies(movies)
    writeActors(actors)
    return movie

def delete_movie(_, info, _id):
    """Delete the movie _id"""
    newLstMovies = []
    movieDeleted = None
    for movie in movies['movies']:
        if movie['id'] == _id:
            movieDeleted = movie
            for actor in getListActors(movie['actors'], actors= actors['actors']):
                actor['films'].remove(_id)
        else :
            newLstMovies.append(movie)
    movies['movies'] = newLstMovies
    writeActors(actors)
    writeMovies(movies)
    return movieDeleted

def create_actor(_, info, _id, _firstname, _lastname, _birthyear, _films):
    """Create an actor using the parameters"""
    actor = {'id': _id, 'firstname': _firstname, 'lastname': _lastname, 'birthyear': _birthyear, 'films': _films}
    if getObjFromListAttr(actors['actors'], 'id', _id) : raise GraphQLError('id already used')
    moviesPlayed = getListMovies(_films, movies['movies'], True)
    for movie in moviesPlayed:
        movie['actors'].append(_id)
    actors['actors'].append(actor)
    writeMovies(movies)
    writeActors(actors)
    return actor

def delete_actor(_, info, _id):
    """Delete the actor _id"""
    newActors = []
    delActor = None
    for actor in actors['actors']:
        if actor['id'] == _id:
            delActor = actor
            for movie in getListMovies(actor['films'], movies['movies']):
                movie['actors'].remove(_id)
        else:
            newActors.append(actor)
    actors['actors'] = newActors
    writeMovies(movies)
    writeActors(actors)
    return delActor

def all_actors(_, info):
    """Get all actors"""
    return actors['actors']

def actor_with_id(_, info, _id):
    """Get the actor having the id _id"""
    return getObjFromListAttr(actors['actors'], 'id', _id)

def add_actor_movie(_, info, _idMovie, _idActor):
    """Add an actor to a movie (and the movie to the actor)"""
    movie = getObjFromListAttr(movies['movies'], 'id', _idMovie)
    if not movie : raise GraphQLError('Unknow movie ' + _idMovie)
    actor = getObjFromListAttr(actors['actors'], 'id', _idActor)
    if not actor : raise GraphQLError('Unknow actor ' + _idActor)
    if _idActor in movie['actors'] and _idMovie in actor['films'] :
            raise GraphQLError('Actor already in the movie')
    if not _idMovie in actor['films'] : actor['films'].append(_idMovie)
    if not _idActor in movie['actors'] : movie['actors'].append(_idActor)
    writeActors(actors)
    writeMovies(movies)
    return movie

def delete_actor_movie(_, info, _idMovie, _idActor):
    """Remove an actor to a movie (and the movie to the actor)"""
    movie = getObjFromListAttr(movies['movies'], 'id', _idMovie)
    if not movie : raise GraphQLError('Unknow movie ' + _idMovie)
    actor = getObjFromListAttr(actors['actors'], 'id', _idActor)
    if not actor : raise GraphQLError('Unknow actor ' + _idActor)
    if not _idActor in movie['actors'] and not _idMovie in actor['films'] :
            raise GraphQLError('Actor not in the movie')
    if _idMovie in actor['films'] : actor['films'].remove(_idMovie)
    if _idActor in movie['actors'] : movie['actors'].remove(_idActor)
    writeActors(actors)
    writeMovies(movies)
    return movie