import json
import time

from graphql import GraphQLError



def movie_with_id(_,info,_id):
    return getObjFromListAttr(readMovies()['movies'], 'id', _id)

#Used for testing and debuging
def syncActorMovie():
    '''Sync actor['films'] -> movie['actor'] if needed'''
    movies = readMovies()
    actors = readActors()
    for actor in actors['actors']:
        for actMovie in actor['films']:
            movieActor = getObjFromListAttr(movies['movies'], 'id', actMovie)
            if movieActor :
                if not (actor['id'] in movieActor['actors']):
                    movieActor['actors'].append(actor['id'])
    writeMovies(movies)


def writeAsJson(filePath, data):
    with open(filePath.format("."), "w") as wfile:
        json.dump(data, wfile)
        wfile.close()

def writeMovies(movies):
    return writeAsJson('{}/data/movies.json', movies)

def writeActors(actors):
    return writeAsJson('{}/data/actors.json', actors)

def readAsJson(filePath):
    with open(filePath.format("."), "r") as rfile:
        jsonData = json.load(rfile)
        rfile.close()
        return jsonData

def readMovies():
    return readAsJson('{}/data/movies.json')

def readActors():
    return readAsJson('{}/data/actors.json')

def getObjFromListAttr(list, attr, val):
   for l in list:
      if l[attr] == val:
         return l
   return None

def getListActors(actorsIds, actors = readActors()['actors'], raiseError = False):
    actorsList = []
    for id in actorsIds:
        actor = getObjFromListAttr(actors, 'id', id)
        if not actor:
            if raiseError: raise GraphQLError('Actor not found ' + id)
        else:
            actorsList.append(actor)
    print("actorLen :" + str(len(actorsList)))
    return actorsList

def resolve_actors_in_movie(movie, info):
    return getListActors(movie['actors'])

def getListMovies(moviesIds, movies = readMovies()['movies'], raiseError = False):
    moviesList = []
    for id in moviesIds:
        movie = getObjFromListAttr(movies, 'id', id)
        if not movie:
            if raiseError: raise GraphQLError('Movie not found ' + id)
        else :
            moviesList.append(movie)
    return moviesList

def resolve_movies_in_actor(actor, info):
    return getListMovies(actor['films'])

def update_movie_rate(_,info,_id,_rate):
    movies = readMovies()
    movie = getObjFromListAttr(movies['movies'], 'id', _id)
    if not movie : raise GraphQLError('Unexisting movie ' + _id)
    movie['rating'] = _rate
    writeMovies(movies)
    return movie

def create_movie(_, info, _id, _title, _director, _rate, _actors):
    movie = {"title": _title, "id": _id, "rating": _rate, "director":_director, "actors":_actors}
    movies = readMovies()
    if getObjFromListAttr(movies['movies'], 'id', _id): raise GraphQLError('id already used')
    actors = readActors()
    actorsPlaying = getListActors(_actors, actors['actors'], True)
    for actor in actorsPlaying:
        actor['films'].append(_id)
    movies['movies'].append(movie)
    writeMovies(movies)
    writeActors(actors)
    return movie

def delete_movie(_, info, _id):
    movies = readMovies()
    newLstMovies = []
    movieDeleted = None
    for movie in movies['movies']:
        if movie['id'] == _id:
            movieDeleted = movie
            actors = readActors()
            for actor in getListActors(movie['actors'], actors= actors['actors']):
                actor['films'].remove(_id)
            writeActors(actors)
        else :
            newLstMovies.append(movie)
    movies['movies'] = newLstMovies
    writeMovies(movies)
    return movieDeleted

def create_actor(_, info, _id, _firstname, _lastname, _birthyear, _films):
    print("Create !!!!!!")
    actor = {'id': _id, 'firstname': _firstname, 'lastname': _lastname, 'birthyear': _birthyear, 'films': _films}
    actors = readActors()
    if getObjFromListAttr(actors['actors'], 'id', _id) : raise GraphQLError('id already used')
    movies = readMovies()
    moviesPlayed = getListMovies(_films, movies['movies'], True)
    for movie in moviesPlayed:
        movie['actors'].append(_id)
    actors['actors'].append(actor)
    writeMovies(movies)
    writeActors(actors)
    return actor

def delete_actor(_, info, _id):
    print("Delete !!!!!!")
    actors = readActors()
    movies = readMovies()
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

def actor_with_id(_, info, _id):
    return getObjFromListAttr(readActors()['actors'], 'id', _id)

def add_actor_movie(_, info, _idMovie, _idActor):
    movies = readMovies()
    actors = readActors()
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
    movies = readMovies()
    actors = readActors()
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