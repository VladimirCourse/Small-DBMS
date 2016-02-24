#include "attribute.h"

Attribute::Attribute(const std::string &name, const std::string &type, const int size){
	_name = name;
	_type = type;
	_size = size;
}

const std::string &Attribute::getType() const{
	return _type;
}

const int Attribute::getSize() const{
	return _size;
}
 
const std::string &Attribute::getName() const{
	return _name;
}
