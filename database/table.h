#include <iostream>
#include <fstream>
#include <vector>
#include "index.h"
#include "attribute.h"

//class of database table
class Table{

private:
	std::string _name;
	std::vector <Attribute> _attributes;	
	std::string _pkey_index_name;
	friend std::istream &operator>>(std::istream &s, Table &table);
	friend std::ostream &operator<<(std::ostream &s, Table &table);
	
public:
	Table();
	Table(const std::string &name);
	void addAttribute(const Attribute &attr);
	void setIndexName(const std::string &index_name);
	const std::string &getName();
	const std::vector<Attribute> &getAttributes() const;
	const bool hasAttribute(const std::string &name) const;
	const int getAttributeSize(const std::string &name) const;
	const std::string getAttributeType(const std::string &name) const;
	const std::string &getPKeyName();
};