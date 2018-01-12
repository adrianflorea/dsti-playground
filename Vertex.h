#include <string>

class Vertex
{
public:
	Vertex(const std::string&);
	std::string getName() const;
	bool operator==(Vertex);
private:
	std::string m_name;
};

struct VertexHash
{
	std::size_t operator()(Vertex const&) const noexcept;
};