#include "index.h"

Index::Index(){
		for (int i = 0; i < MAX_INDEX_SIZE; i++){
		_index_table[i] = 0;
	}
	_offset = 0;
}

Index::Index(const std::string &name, const std::string &table_name){
	_name = name;
	_table_name = table_name;
	for (int i = 0; i < MAX_INDEX_SIZE; i++){
		_index_table[i] = 0;
	}
	_offset = 0;
}
//input from file
std::istream &operator>>(std::istream &s, Index &index){
	s >> index._name >> index._table_name;
	int count = 0;
	s >> count;
	std::string attr;
	for (int i = 0; i < count; i++){
		s >> attr;
		index._attributes.push_back(attr);
	}
	for (int i = 0; i < MAX_INDEX_SIZE; i++){
		index._index_table[i] = 0;
	}
	unsigned long long x;
	for (int i = 0; i < MAX_INDEX_SIZE; i++){
		s >> index._index_table[i];
	}
	return s;
}
//output to file
std::ostream &operator<<(std::ostream &s, Index &index){
	s << index._name << " " << index._table_name << " ";
	s << index._attributes.size() << " ";
	for (auto it = begin(index._attributes); it != end(index._attributes); it++){
		s << *it << " ";
	}
	for (int i = 0; i < MAX_INDEX_SIZE; i++){
		if (index._index_table[i] != 0) index._index_table[i] += index._offset;
		s << intToStr(16, index._index_table[i]) << " ";
	}
	index._offset = 0;
	return s;
}

const std::string &Index::getName() const{
	return _name;
}

const std::string &Index::getTableName() const{
	return _table_name;
}

void Index::addAttribute(const std::string &attr){
	_attributes.push_back(attr);
}

void Index::updateOffset(const unsigned long long offset){
	_offset = offset;
}

const unsigned long long Index::getRecOffset(const int hash) const{
	return _index_table[hash];
}

bool Index::attributesCheck(const std::vector<std::string> &to_check){
	return _attributes == to_check;
}

void Index::update(const unsigned long long hash, const unsigned long long offset){
	_index_table[hash] = offset;
}

const std::vector <std::string> &Index::getAttributes() const{
	return _attributes;
}