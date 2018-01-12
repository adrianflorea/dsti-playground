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

bool Graph::areConnected(const std::string& vertex1, const std::string& vertex2) const
{
	// BFS-based implementation

	std::unordered_map<std::string, bool> visited;
	std::queue<std::string> queue;
	for (const auto& iterator : adjacencyList)
	{
		visited.emplace(iterator.first, false);
	}

	visited[vertex1] = true;
	queue.push(vertex1);

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
			if (neighbour == vertex2)
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

void Graph::printAdjacencies() const
{
	for (const auto& iterator : adjacencyList)
	{
		std::cout << iterator.first << ":";
		std::copy(iterator.second.begin(), iterator.second.end(), 
			std::ostream_iterator<std::string>(std::cout, " "));
		std::cout << std::endl;
	}
}