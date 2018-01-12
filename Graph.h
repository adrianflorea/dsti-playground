#include <utility>
#include <list>
#include <unordered_map>
#include "Vertex.h"

class Graph
{
public:
	Graph() = default;
	void addVertex(const std::string&);
	void removeVertex(const std::string&);
	void addEdge(const std::string&, const std::string&);
	void removeEdge(const std::string&, const std::string&);
	int getVerticesCount() const;
	int getEdgesCount() const;
	int getInDegree(const std::string&) const;
	int getOutDegree(const std::string&) const;
	std::list<std::string> getNeighbourhood(const std::string&) const;
	bool isEdge(const std::string&, const std::string&) const;
	bool areConnected(const std::string&, const std::string&) const;
	void printAdjacencies() const;
private:
	using AdjacencyList = std::unordered_map<std::string, std::list<std::string>>;

	AdjacencyList adjacencyList;
};