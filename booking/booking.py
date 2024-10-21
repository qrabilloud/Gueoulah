import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2_grpc
import showtime_pb2
import super_pb2
import json

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        self.update()

    def getPlannedMovies(self, date):
        """Returns the list of movies planned for a specific date by interrogating the schedule."""
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowTimeStub(channel)
            print(stub)
            print("-------------- GetPlannedMovies --------------")
            schedule = stub.GetMovieByDate(showtime_pb2.MovieDate(date=date)).movies
            print("Everything is going great.")
        channel.close()
        return schedule

    def update(self):
        "Updates the value of the database field to match the potential changes made in the file."
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def write(self):
        with open('{}/data/bookings.json'.format("."), 'w') as f:
            json.dump({"bookings" : self.db}, f)

    def GetBookings(self, request, context):
        """Gives a list of users with the associated bookings, say all the current bookings."""
        self.update()
        result = []
        for booking in self.db:
            for showtime in booking['dates']:
                result.append(booking_pb2.BookingData(userid=booking['userid'], date=super_pb2.TimeShow(date=showtime['date'], movies=showtime['movies'])))
        return booking_pb2.Bookings(bookings=result)
        
    def GetBookingsByUser(self, request, context):
        self.update()
        """Gives a stream of bookings for a given user."""
        for booking in self.db:
            if booking['userid'] == request.userid:
                return booking_pb2.Bookings(bookings=[booking_pb2.BookingData(userid=booking['userid'], date=super_pb2.TimeShow(date=showtime['date'], movies=showtime['movies'])) for showtime in booking['dates']])
        print("This user does not have any bookings yet.")
        return booking_pb2.Bookings(bookings=[])
    
    def _bookingsByUser(self, userid):
        return [userBookings['dates'] for userBookings in self.db if userBookings['userid'] == userid][0]
    
    def AddBookingByUser(self, request, context):
        """Adds a booking for an already existing user."""
        moviesOnRequestedDate = self.getPlannedMovies(request.date.date)
        print(moviesOnRequestedDate)
        availableMovies = [wantedMovie for wantedMovie in request.date.movies if wantedMovie in moviesOnRequestedDate]
        userBookingsForRequestedDate = [booking['movies'] for booking in self._bookingsByUser(request.userid) if booking['date'] == request.date.date][0]
        moviesToBook = [movie for movie in availableMovies if movie not in userBookingsForRequestedDate]
        existingDate = False
        for user in self.db:
            if user['userid'] == request.userid:
                for booking in user['dates']:
                    if booking['date'] == request.date.date:
                        existingDate |= True
                        booking['movies'] += moviesToBook
                if not existingDate:
                    user['dates'].append({"date": request.date.date, "movies": moviesToBook})
        self.write()
        return super_pb2.Empty()
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()

#def get_schedule(stub):
#    schedule = stub.GetSchedule(showtime_pb2.Empty())
#    for timeshow in schedule:
#        print("The {} there are the following movies {}".format(timeshow.date,timeshow.movies))

if __name__ == '__main__':
    serve()
