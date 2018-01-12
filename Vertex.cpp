#include "Vertex.h"

Vertex::Vertex(const std::string& name) : m_name{ name } {}

std::string Vertex::getName() const {return m_name;}

bool Vertex::operator==(Vertex v)
{
	return m_name == v.getName();
}

std::size_t VertexHash::operator()(Vertex const& v) const noexcept
{
	return std::hash<std::string>{}(v.getName());
}