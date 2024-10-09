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
    def GetBookings(self, request, context):
        """Gives a stream of users with the associated list of bookings, say all the current bookings."""
        for booking in self.db:
            for showtime in booking['dates']:
                yield booking_pb2.BookingData(userid=booking['userid'], date=super_pb2.TimeShow(date=showtime['date'], movies=showtime['movies']))
    def GetBookingsByUser(self, request, context):
        """Gives a stream of bookings for a given user."""
        isMet = False
        for booking in self.db:
            if booking['userid'] == request.userid:
                for showtime in booking['dates']:
                    isMet |= True
                    yield booking_pb2.BookingData(userid=booking['userid'], date=super_pb2.TimeShow(date=showtime['date'], movies=showtime['movies']))
        if not isMet:
            print("Such user does not exist")
            #TODO : add a gRPC error in the context management
    def AddBookingByUser(self, request, context):
        pass
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

#def get_schedule(stub):
#    schedule = stub.GetSchedule(showtime_pb2.Empty())
#    for timeshow in schedule:
#        print("The {} there are the following movies {}".format(timeshow.date,timeshow.movies))

if __name__ == '__main__':
    serve()
