import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json

class ShowTimeServicer(showtime_pb2_grpc.ShowTimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]
    
    def GetSchedule(self, request, context):
        """Gives a stream of dates with the associated list of movies, say the whole schedule."""
        for showtime in self.db:
            yield showtime_pb2.TimeShow(date=showtime['date'], movies=showtime['movies'])
    def GetMovieByDate(self, request, context):
        """Takes a date in entry and returns all the movies scheduled for this date. Returns an
        empty list if there are no movies for the date specified."""
        for showtime in self.db:
            if showtime['date'] == request.date:
                return showtime_pb2.MovieID(movies=showtime['movies'])
        return showtime_pb2.MovieID(movies=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowTimeServicer_to_server(ShowTimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
