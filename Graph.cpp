#include <utility>
#include <numeric>
#include <algorithm>
#include <queue>
#include <iterator>
#include <iostream>
#include "Graph.h"

void Graph::addVertex(const std::string& vertex)
{
	adjacencyList.try_emplace(vertex, std::list<std::string>{});
}

void Graph::removeVertex(const std::string& vertex)
{
	for (auto& iterator : adjacencyList)
	{
		iterator.second.remove(vertex);
	}
	adjacencyList.erase(vertex);
}

void Graph::addEdge(const std::string& origin, const std::string& destination)
{
	adjacencyList.try_emplace(origin, std::list<std::string>{});
	adjacencyList.try_emplace(destination, std::list<std::string>{});
	adjacencyList[origin].push_back(destination);
}

void Graph::removeEdge(const std::string& origin, const std::string& destination)
{
	auto& originFound = adjacencyList.find(origin);
	if (originFound != adjacencyList.end())
	{
		auto& originNeighbours = originFound->second;
		auto& destinationFound = std::find(originNeighbours.begin(), originNeighbours.end(), 
			destination);
		if (destinationFound != originNeighbours.end())
		{
			adjacencyList[origin].remove(destination);
		}
	}
}

int Graph::getVerticesCount() const
{
	return adjacencyList.size();
}

int Graph::getEdgesCount() const
{
	auto edgesCount = 0;
	for (const auto& iterator : adjacencyList)
		edgesCount += iterator.second.size();
	return edgesCount;
}

int Graph::getInDegree(const std::string& vertex) const
{
	auto inDegree = 0;
	for (const auto& iterator : adjacencyList)
	{
		inDegree += std::count(iterator.second.begin(), iterator.second.end(), vertex);
	}
	return inDegree;
}

int Graph::getOutDegree(const std::string& vertex) const
{
	auto outDegree = 0;
	auto& found = adjacencyList.find(vertex);
	if (found != adjacencyList.end()) 
	{
		outDegree = found->second.size();
	}
	return outDegree;
}

std::list<std::string> Graph::getNeighbourhood(const std::string& vertex) const
{
	std::list<std::string> neighbourhood;
	auto& found = adjacencyList.find(vertex);
	if (found != adjacencyList.end())
	{
		auto& neighbours = found->second;
		std::copy(neighbours.begin(), neighbours.end(), std::back_inserter(neighbourhood));
	}
	return neighbourhood;
}

bool Graph::isEdge(const std::string& origin, const std::string& destination) const
{
	auto& neighbourhood = getNeighbourhood(origin);
	auto& found = std::find(neighbourhood.begin(), neighbourhood.end(), destination);
	if (found != neighbourhood.end())
	{
		return true;
	}
	return false;
}

bool Graph::areConnected(const std::string& origin, const std::string& destination) const
{
	// BFS-based implementation

	std::unordered_map<std::string, bool> visited;
	std::queue<std::string> queue;
	for (const auto& iterator : adjacencyList)
	{
		visited.emplace(iterator.first, false);
	}

	visited[origin] = true;
	queue.push(origin);

	while (!queue.empty())
	{
		auto v = queue.front();
		queue.pop();

		// "at" instead of "operator[]" 
		// because "at" is a const function
		// and "operator[]" is not
		// (const required by the const signature of "areConnected")
		for (const auto& neighbour : adjacencyList.at(v))
		{
			if (neighbour == destination)
				return true;
			if (!visited[neighbour])
			{
				visited[neighbour] = true;
				queue.push(neighbour);
			}
		}
	}
	return false;
}

std::list<std::string> Graph::getShortestPath(const std::string& origin, const std::string& destination) const
{
	if (!areConnected(origin, destination))
	{
		throw std::invalid_argument("The vertices \'" + origin + "\' and \'" + destination + "\' are not connected!");
	}
	
	std::unordered_map<std::string, int> distance;
	std::unordered_map<std::string, std::string> predecessor;
	for (const auto& iterator : adjacencyList)
	{
		// the return value of std::numeric_limits<int>::infinity() is 0
		// so I use std::numeric_limits<int>::max() instead
		distance.emplace(iterator.first, std::numeric_limits<int>::max());
		predecessor.emplace(iterator.first, "");
	}

	// BFS is Dijkstra for unweighted graphs with 
	// std::queue (FIFO) instead of std::priority_queue
	// implemented here as Dijkstra as a learning exercise 
	
	using QueueItem = std::pair<std::string, int>;
	auto& greater = [](const QueueItem& item1, const QueueItem& item2) {return item1.second > item2.second; };
	std::priority_queue<QueueItem, std::vector<QueueItem>, decltype(greater)> priorityQueue(greater);

	distance[origin] = 0;
	priorityQueue.push(std::make_pair(origin, distance[origin]));

	while (!priorityQueue.empty())
	{
		std::string u = priorityQueue.top().first;
		priorityQueue.pop();

		for (const auto& v : adjacencyList.at(u))
		{
			// unweighted graph means all "weights" are 1
			if(distance[u] + 1 < distance[v])
			{
				distance[v] = distance[u] + 1;
				predecessor[v] = u;
				// stop traversal
				if (v == destination)
				{
					// clear the queue
					while (!priorityQueue.empty())
					{
						priorityQueue.pop();
					}
					break;
				}
				priorityQueue.push(std::make_pair(v, distance[v]));
			}
		}
	}

	std::list<std::string> shortestPath;
	auto vertex = destination;
	shortestPath.push_back(vertex);
	while (vertex != origin)
	{
		shortestPath.push_back(vertex = predecessor[vertex]);
	}
	shortestPath.reverse();
	return shortestPath;
}

void Graph::printVertices(const std::list<std::string>& vertices) const
{
	std::copy(vertices.begin(), vertices.end(), 
		std::ostream_iterator<std::string>(std::cout, " "));
	std::cout << std::endl;
}

void Graph::printAdjacencies() const
{
	for (const auto& iterator : adjacencyList)
	{
		std::cout << iterator.first << ":";
		printVertices(iterator.second);
	}
}