import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2_grpc
import showtime_pb2
import json

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

def get_schedule(stub):
    schedule = stub.GetSchedule(showtime_pb2.Empty())
    for timeshow in schedule:
        print("The {} there are the following movies {}".format(timeshow.date,timeshow.movies))

def run():
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = showtime_pb2_grpc.ShowTimeStub(channel)

        print("-------------- GetSchedule --------------")
        get_schedule(stub)
    channel.close()

if __name__ == '__main__':
    run()
