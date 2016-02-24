#include "table.h"

Table::Table(){

}

Table::Table(const std::string &name){
	_name = name;
}

void Table::addAttribute(const Attribute &attr){
	_attributes.push_back(attr);
}

void Table::setIndexName(const std::string &index_name){
	_pkey_index_name = index_name;
}
//output
std::istream& operator>>(std::istream &s, Table &table){
	s >> table._name;
	int count = 0;
	s >> count;
	std::string name;
	std::string type;
	int size;
	for (int i = 0; i < count; i++){
		s >> name >> type >> size;
		table._attributes.push_back(Attribute(name, type, size));
	}
	s >> table._pkey_index_name;
	return s;
}
//input
std::ostream &operator<<(std::ostream &s, Table &table){
	s << table._name << " ";
	s << table._attributes.size() << " ";
	for (auto it = begin(table._attributes); it != end(table._attributes); it++){
		s << it->getName() << " " << it->getType() << " " << it->getSize() << " ";
	}
	s << table._pkey_index_name << " ";
	return s;
}

const std::string &Table::getName(){
	return _name;
}

const std::vector<Attribute> &Table::getAttributes() const{
	return _attributes;
}
//getters for attributes
const bool Table::hasAttribute(const std::string &name) const{
	for (auto it = begin(_attributes); it != end(_attributes); it++){
		if (it->getName() == name) return true;
	}
	return false;
}

const int Table::getAttributeSize(const std::string &name) const{
	for (auto it = begin(_attributes); it != end(_attributes); it++){
		if (it->getName() == name) return it->getSize();
	}
	return -1;
}

const std::string Table::getAttributeType(const std::string &name) const{
	for (auto it = begin(_attributes); it != end(_attributes); it++){
		if (it->getName() == name) return it->getType();
	}
	return "";
}

const std::string &Table::getPKeyName(){
	return _pkey_index_name;
}