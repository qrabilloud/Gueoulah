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
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def getPlannedMovies(self):
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowTimeStub(channel)
            print(stub)
            print("-------------- GetPlannedMovies --------------")
            schedule = stub.GetSchedule(super_pb2.Empty())
            print("Everything is going great.")
        channel.close()
        return schedule

    def write(self):
        with open('{}/data/bookings.json'.format("."), 'w') as f:
            json.dump({"bookings" : self.db}, f)

    def GetBookings(self, request, context):
        """Gives a list of users with the associated bookings, say all the current bookings."""
        result = []
        for booking in self.db:
            for showtime in booking['dates']:
                result.append(booking_pb2.BookingData(userid=booking['userid'], date=super_pb2.TimeShow(date=showtime['date'], movies=showtime['movies'])))
        return booking_pb2.Bookings(bookings=result)
        
    def GetBookingsByUser(self, request, context):
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
        print("Beginning of the call")
        moviesOnRequestedDate = [show.movies for show in self.getPlannedMovies().schedule if show.date == request.date.date][0]
        availableMovies = [wantedMovie for wantedMovie in request.date.movies if wantedMovie in moviesOnRequestedDate]
        print(availableMovies)
        userBookingsForRequestedDate = [booking['movies'] for booking in self._bookingsByUser(request.userid) if booking['date'] == request.date.date][0]
        print(userBookingsForRequestedDate)
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
