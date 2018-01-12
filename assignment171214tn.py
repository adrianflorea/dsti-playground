import heapq
import collections
import urllib.parse, urllib.request
import json


class Station:
    def __init__(self, station_id, station_name, station_lat=None, station_lng=None):
        self._station_id = station_id
        self._station_name = station_name
        self._station_lat = station_lat
        self._station_lng = station_lng

    def get_id(self):
        return self._station_id

    def get_name(self):
        return self._station_name

    def load_lat_lng(self):
        self._station_lat, self._station_lng = TransportNetwork.get_lat_lng(self._station_name)

    def get_lat(self):
        return self._station_lat

    def get_lng(self):
        return self._station_lng

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(self._station_id, self._station_name)


class LineSegment:
    def __init__(self,
                 origin_station_id, destination_station_id, duration):
        self._origin_station_id = origin_station_id
        self._destination_station_id = destination_station_id
        self._duration = duration

    def get_origin_station_id(self):
        return self._origin_station_id

    def get_destination_station_id(self):
        return self._destination_station_id

    def get_duration(self):
        return self._duration

    # required to work with PriorityQueue
    def __lt__(self, other):
        return self._duration < other._duration

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash((
            self._origin_station_id,
            self._destination_station_id,
            self._destination))

# important to have duration the first element of the tuple!
# it will be the priority of the PriorityQueue
Route = collections.namedtuple("Route" , "duration path")
LatLng = collections.namedtuple("LatLng" , "lat lng")


class TransportNetwork:
    def __init__(self):
        self._stations = {}
        self._adjaceny_list = {}
        self._locations = {}

    def add_station(self, station_id, station_name, station_lat=None, station_lng=None):
        self._stations[station_id] = station_name
        self._adjaceny_list[station_id] = []
        self._locations[station_id] = LatLng(lat=station_lat, lng=station_lng)

    def add_line_segment(self,
                         origin_station_id,
                         destination_station_id,
                         duration):
        line_segment = LineSegment(
            origin_station_id=origin_station_id,
            destination_station_id=destination_station_id,
            duration=duration)
        self._adjaceny_list[origin_station_id].append(line_segment)
        self._adjaceny_list[destination_station_id].append(line_segment)

    def _parse_station(self, text):
        station_id, station_name = text.split(" ", 1)
        station_id = station_id.lstrip("0")
        station_name = station_name.strip()
        if station_id == "":
            station_id = "0"
        return Station(station_id=station_id, station_name=station_name)

    def _parse_line_segment(self, text):
        origin_station_id, destination_station_id, duration =\
            text.split(" ", 2)
        duration = float(duration.strip())
        return LineSegment(
            origin_station_id=origin_station_id,
            destination_station_id=destination_station_id,
            duration=duration)

    def load_from_file(self, file_name):
        file = open(file_name, mode="r")
        loading_target = None
        for line_in_file in file:
            if line_in_file.strip() == "[Vertices]":
                loading_target = Station.__name__
                continue
            elif line_in_file.strip() == "[Edges]":
                loading_target = LineSegment.__name__
                continue
            elif loading_target == Station.__name__:
                station = self._parse_station(line_in_file)
                # station.load_lat_lng()
                self.add_station(
                    station.get_id(),
                    station.get_name(),
                    station.get_lat(),
                    station.get_lng())
                continue
            elif loading_target == LineSegment.__name__:
                line_segment = self._parse_line_segment(line_in_file)
                self.add_line_segment(
                    line_segment.get_origin_station_id(),
                    line_segment.get_destination_station_id(),
                    line_segment.get_duration())
                continue
            else:
                raise ValueError("Invalid file format! - %s" % file_name)

    def adjacent_stations(self, station_id):
        adjacent_stations = set([])
        for line_segment in self._adjaceny_list[station_id]:
            adjacent_stations.update([line_segment.get_origin_station_id()])
            adjacent_stations.update([line_segment.get_destination_station_id()])
        adjacent_stations.difference_update([station_id])
        for line_segment in self._adjaceny_list[station_id]:
            if line_segment.get_origin_station_id() == station_id and\
                line_segment.get_destination_station_id() in adjacent_stations:
                    yield line_segment.get_destination_station_id(), line_segment.get_duration()

    def get_line_segment_duration(self, station_id, next_station_id):
        for line_segment in self._adjaceny_list[station_id]:
            if line_segment.get_origin_station_id() == station_id and\
                line_segment.get_destination_station_id() == next_station_id:
                return line_segment.get_duration()
            else:
                continue

    def get_station_name(self, station_id):
        return self._stations[station_id]

    def get_quickest_path_by_station_ids(self, origin_station_id, destination_station_id):
        priority_queue = PriorityQueue()

        for station_id, duration in self.adjacent_stations(origin_station_id):
            priority_queue.push(Route(duration=float(duration), path=[origin_station_id, station_id]))
        visited = set([origin_station_id])

        while priority_queue:
            duration, path = priority_queue.pop()
            next_station_id = path[-1]
            if next_station_id in visited:
                continue
            if next_station_id == destination_station_id:
                return duration, path

            for station_id, new_duration in self.adjacent_stations(next_station_id):
                if station_id not in visited:
                    new_duration = float(new_duration) + float(duration)
                    new_path = path + [station_id]
                    priority_queue.push(Route(duration=float(new_duration), path=new_path))
            visited.add(next_station_id)
        return float("inf"), new_path

    def get_station_ids(self, station_name):
        for station_id in self._stations:
            if self._stations[station_id] == station_name:
                yield station_id

    def get_quickest_path_by_station_names(self, origin_station_name, destination_station_name):
        priority_queue = PriorityQueue()
        for origin_station_id in self.get_station_ids(origin_station_name):
            for destination_station_id in self.get_station_ids(destination_station_name):
                duration, path = self.get_quickest_path_by_station_ids(origin_station_id, destination_station_id)
                priority_queue.push(Route(duration=float(duration), path=path))
        if priority_queue:
            quickest_duration, quickest_path = priority_queue.pop()
            return quickest_duration, quickest_path
        else:
            return float("inf"), None

    def get_google_places_url(station_name):
        # error "You have exceeded your daily request quota for this API"
        google_places_api_key = "YOURGOOGLEPLACESAPIKEY"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        url = url + "?key=" + google_places_api_key
        url = url + "&query=" + urllib.parse.quote(station_name) + "&sensor=false"
        url = url + "&types=" + urllib.parse.quote("subway_station")
        return url

    def get_lat_lng(station_name):
        request = urllib.request.urlopen(TransportNetwork.get_google_places_url(station_name))
        response = json.loads(request.read().decode())
        print(response)
        if len(response["results"]) > 0:
            return response["results"][0]["geometry"]["location"]["lat"],\
                response["results"][0]["geometry"]["location"]["lng"]
        else:
            return None, None

    def save_station_locations_to_file(self, file_name):
        file = open(file_name, mode="w")
        for station_id in self._stations:
            lat, lng = TransportNetwork.get_lat_lng(self._stations[station_id])
            file.write("%s %s %s\n" % (station_id, lat, lng))
        file.close()

class PriorityQueue:
    def __init__(self):
        self._values = []

    def push(self, value):
        heapq.heappush(self._values, value)

    def pop(self):
        return heapq.heappop(self._values)

    # required by "while priority_queue:" loop
    def __len__(self):
        return len(self._values)

"""
Course:  Algorithmics for Data Science - Optimisation - A17 @ DSTI
Instructor: Dr. Amir Nakib
Student: Adrian Florea

Assignment: 3 - Metro transportation problem
Due date: December 14th, 2017, 11:55 PM CET

Design an algorithm on python or c++ that allows to calculate 
the shortest and the quickest path 
from one given metro station to another metro station (destination).
"""

def main():
    paris_metro = TransportNetwork()
    paris_metro.load_from_file("./metro_complet.txt")

    origin_station_name = input("The quickest path between the station: ")
    destination_station_name = input("and the station: ")
    print("is:\n")
    duration, path = paris_metro.get_quickest_path_by_station_names(origin_station_name, destination_station_name)
    if duration == float("inf"):
        print("No path found between the stations %s and %s!" % (origin_station_name, destination_station_name))
    else:
        for station_id in path:
            print("%s %s" % (station_id, paris_metro.get_station_name(station_id)))
        print("\n")
        print("Total duration of the trip: %.0f seconds" % duration)

if __name__ == "__main__":
    main()