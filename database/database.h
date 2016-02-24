#include <iostream>
#include <fstream>
#include <time.h>
#include "table.h"

//class with main database operations
class Database{

private:
	//data
	std::string _file_name;
	std::ifstream _file;
	std::ofstream _log;
	std::string _name;
	std::vector <Table> _tables;
	std::vector<Index> _indexes;
	unsigned long long _data_begin;
	unsigned long long _indexes_begin;
	//methods
	Table *findTable(const std::string &name);
	bool parseCreateIndex(const std::vector<std::string> &tokens, int start);
	bool parseCreateTable(const std::vector<std::string> &tokens, int start);
	bool parseInsert(const std::vector<std::string> &tokens, int start);
	std::string *parseJoin(const std::vector<std::string> &tokens, int start);
	std::vector <std::map <std::string, std::string> > *parseSelect(const std::vector<std::string> &tokens, int start);
	std::map <std::string, std::string> select(const Table &table, unsigned long long hash_int);
	bool isWhereFound(const Table &table, const std::map <std::string, std::string> &where, std::map <std::string, std::string> &data);
	void updateFile();
	void writeToFile(const std::string &str);
public:
	Database(const std::string &file_name);
	std::string *request(const std::string &req);

};