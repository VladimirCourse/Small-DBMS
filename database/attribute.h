#include "helpers.h"

//attribute class
class Attribute{

private:
	std::string _type;
	int _size;
	std::string _name;

public:
	Attribute(const std::string &name, const std::string &type, const int size);
	const std::string &getType() const;
	const int getSize() const;
	const std::string &getName() const;

};