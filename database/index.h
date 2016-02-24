#include <iostream>
#include <vector>
#include <functional>
#include <map>
#include "helpers.h"

//class of database index
class Index{

private:
	std::string _name;
	std::string _table_name;
	std::vector <std::string> _attributes;
	unsigned long long _offset;
	unsigned long long _index_table[MAX_INDEX_SIZE];
	friend std::istream &operator>>(std::istream &s, Index &index);
	friend std::ostream &operator<<(std::ostream &s, Index &index);

public:
	Index();
	Index(const std::string &name, const std::string &table_name);
	void updateOffset(const unsigned long long offset);
	void addAttribute(const std::string &attr);
	const std::string &getName() const;
	const std::string &getTableName() const;
	const unsigned long long getRecOffset(const int hash) const;
	bool attributesCheck(const std::vector<std::string> &to_check);
	void update(const unsigned long long hash, const unsigned long long offset);
	const std::vector <std::string> &getAttributes() const;
};