#include "database.h"

//constructor, getting all information about database from file
Database::Database(const std::string &file_name){
	_file_name = file_name;
	_file.open(file_name.c_str(), std::ifstream::in);
	_log.open((file_name + ".log").c_str(), std::ifstream::out | std::ofstream::app);
	_file >> _name;
	int count = 0;
	//fetch all tables
	_file >> count;
	for (int i = 0; i < count; i++){
		Table res;
		_file >> res;
		_tables.push_back(res);
	}
	//fetch all indexes
	_indexes_begin = _file.tellg();
	_file >> count;
	Index index;
	for (int i = 0; i < count; i++){
		_file >> index;
		_indexes.push_back(index);
	}
	_data_begin = 1 + _file.tellg();
}
//create indexes
bool Database::parseCreateIndex(const std::vector<std::string> &tokens, int start){
	//check for valid names
	if (!isValidName(tokens[start])) return false;
	for (auto it = begin(_indexes); it != end(_indexes); it++){
		if (it->getName() == tokens[start]) return false;
	}
	//find table
	for (auto it = begin(_tables); it != end(_tables); it++){
		if (it->getName() == tokens[start + 1]){
			//create index
			Index new_index(tokens[start], tokens[start + 1]);
			std::vector <std::string> vals = split(tokens[start + 2], ',');
			for (auto it2 = begin(vals); it2 != end(vals); it2++){
				if (it->hasAttribute(*it2)){
					new_index.addAttribute(*it2);
					continue;
				}
				else return false;
			}
			_indexes.push_back(new_index);
			return true;
		}
	}
	return false;
}
//create table
bool Database::parseCreateTable(const std::vector<std::string> &tokens, int start){
	//check for valid names
	if (!isValidName(tokens[start])) return false;
	for (auto it = begin(_tables); it != end(_tables); it++){
		if (it->getName() == tokens[start]) return false;
	}
	std::vector <std::string> vals = split(tokens[start + 1], ',');
	Table new_table(tokens[start]);
	for (int i = 0; i < vals.size(); i += 3){
		new_table.addAttribute(Attribute(vals[i], vals[i + 1], std::stoi(vals[i + 2])));
	}
	//create index for primary key
	std::vector<std::string> index_tokens(tokens.begin() + start + 3, tokens.end());
	new_table.setIndexName(index_tokens[0]);
	_tables.push_back(new_table);
	index_tokens.insert(index_tokens.begin() + 1, tokens[start]);
	return parseCreateIndex(index_tokens, 0);
}
//rewriting header to file, useing temporary file
void Database::updateFile(){
	std::ofstream file("tmp", std::ifstream::out);
	file << _name << " ";
	//write tables
	file << _tables.size() << " ";
	for (auto it = begin(_tables); it != end(_tables); it++){
		file << *it;
	}
	//write idexes
	_indexes_begin = file.tellp();
	file << _indexes.size() << " ";
	for (auto it = begin(_indexes); it != end(_indexes); it++){
		file << *it;
	}
	//update offset of indexes if need it
	unsigned long long offset = file.tellp();
	offset -= _data_begin;
	file.seekp(_indexes_begin, std::ios_base::beg);
	file << _indexes.size() << " ";
	for (auto it = begin(_indexes); it != end(_indexes); it++){
		it->updateOffset(offset);
		file << *it;
	}
	//write data from rest of file
	_file.seekg(_data_begin, std::ios_base::beg);
	_data_begin = 1 + file.tellp();
	file << _file.rdbuf();
	_file.close();
	file.close();
	remove(_file_name.c_str());
	rename("tmp", _file_name.c_str());
	_file.open(_file_name.c_str(), std::ifstream::in);
}
//append string to file
void Database::writeToFile(const std::string &str){
	_file.close();
	std::ofstream file(_file_name, std::ifstream::out | std::ofstream::app);
	file.seekp(0, std::ios_base::end);
	file << str;
	file.close();
	_file.open(_file_name, std::ifstream::in);

}
//returns map <attr, value>, reading record from file
std::map <std::string, std::string> Database::select(const Table &table, unsigned long long offset){
	std::map <std::string, std::string> result;
	_file.seekg(offset, std::ios_base::beg);
	const std::vector <Attribute> attrs = table.getAttributes();
	//read all attributes
	for (auto it = begin(attrs); it != end(attrs); it++){
		char * buf = new char[it->getSize()];
		_file.read(buf, it->getSize());
		buf[it->getSize()] = '\0';
		std::string str = buf;
		str = trim(str);
		if (str.size() == 0) str = "No data";
		result[it->getName()] = str;
	}
	return result;
}

//its kind of magic (∩｀-´)⊃━☆ﾟ.*･｡ﾟ, don't read this
std::string *Database::parseJoin(const std::vector<std::string> &tokens, int start){
	std::vector <std::string>::const_iterator find_limit = std::find(tokens.begin(), tokens.end(), "LIMIT");
	int limit = -1, offset = 0, ended = 0, count = 0;
	std::string *result = new std::string();
	if (find_limit != tokens.end()){
		find_limit++;
		offset = std::stoi(*find_limit);
		limit = std::stoi(*(find_limit + 1));
	}
	//you can lose your sanity, DON'T READ THIS PLEASE
	std::vector <std::map <std::string, std::string> > *res, *tmp;
	std::vector <std::string> vals = split(tokens[start], ',');
	std::vector <std::string>::const_iterator find_order = std::find(tokens.begin(), tokens.end(), "ORDER");
	std::map <std::string, std::string> sorted;
	std::vector <std::string>::const_iterator find = std::find(tokens.begin(), tokens.end(), "JOIN");
	//parsing join
	if (find != tokens.end()){
		std::vector<std::string> to;
		to.push_back("*");
		to.push_back("FROM");
		std::vector <std::string>::const_iterator find_where = std::find(tokens.begin(), tokens.end(), "WHERE");
		std::vector <std::string> on = split(*(std::find(tokens.begin(), tokens.end(), "ON") + 1), '=');
		//I TOLD YOU
		while (find != tokens.end()){
			to.push_back(*(find + 1));
			if (find_where != tokens.end()){
				to.push_back(*find_where);
				to.push_back(*(find_where + 1));
			}
			res = parseSelect(to, 0);
			if (find_where != tokens.end()){
				to.pop_back();
				to.pop_back();
			}
			to.pop_back();
			to.push_back(tokens[start + 2]);
			to.push_back("WHERE");
			//GO BACK PLEASE, IT'S MADNESS
			for (auto it = begin(*res); it != end(*res); it++){
				to.push_back(on[0] + "=" + (*it)[on[1]]);
				tmp = parseSelect(to, 0);
				for (auto it2 = begin(*tmp); it2 != end(*tmp); it2++){
					if (offset != 0){
						offset--;
						continue;
					}
					if (vals[0] == "*"){
						for (auto it3 = begin(*it); it3 != end(*it); it3++){
							result->append(it3->second);
							result->append("$$$");
						}
						for (auto it3 = begin(*it2); it3 != end(*it2); it3++){
							result->append(it3->second);
							result->append("$$$");
						}
					}else if (tokens[1] != "COUNT(*)"){
						for (auto val = begin(vals); val != end(vals); val++){
							result->append((*it)[*val]);
							result->append((*it2)[*val]);
							result->append("$$$");
						}
					}
					//ARE YOU STILL ALIVE?
					result->append("###");
					count++;
					if (limit != -1){
						if (count == limit){
							ended = 1;
							break;
						}
					}
				}				
				to.pop_back();
				delete tmp;
				if (ended) break;
			}

			find = std::find(find + 1, tokens.end(), "JOIN");
		}
	//IT IS NOT THE END
	}else{
		//parsing simple select
		res = parseSelect(tokens, start);
		for (auto it = begin(*res); it != end(*res); it++){
			if (offset != 0){
				offset--;
				continue;
			}
			std::string sorted_tmp;
			if (vals[0] == "*"){
				for (auto it2 = begin(*it); it2 != end(*it); it2++){
					if (find_order != tokens.end()){
						sorted_tmp.append(it2->second);
						sorted_tmp.append("$$$");
					}else{
						result->append(it2->second);
						result->append("$$$");
					}
				}
			}else if (tokens[1] != "COUNT(*)"){
				for (auto val = begin(vals); val != end(vals); val++){
					if (find_order != tokens.end()){
						sorted_tmp.append((*it)[*val]);
						sorted_tmp.append("$$$");
					}else{
						result->append((*it)[*val]);
						result->append("$$$");
					}
				}
			}
			//YOU DID THIS, WELCOME TO LAST CIRCLE OF HELL
			if (find_order != tokens.end()) sorted[(*it)[*(find_order + 1)]] = sorted_tmp;
			else result->append("###");
			count++;
			if (limit != -1){
				if (count == limit){
					ended = 1;
					break;
				}
			}			
			if (ended) break;
		}
	}
	//count 
	if (tokens[1] == "COUNT(*)") result->append(std::to_string(count));
	else if (find_order != tokens.end()){
		//sorting
		int sort_type = 0;
		if ((find_order + 2) != tokens.end()){
			if (*(find_order + 2) == "desc") sort_type = 1;
		}
		if (sort_type == 0){
			for (auto it = begin(sorted); it != end(sorted); it++){
				result->append(it->second);
				result->append("###");
			}
		}else{
			for (auto it = sorted.rbegin(); it != sorted.rend(); it++){
				result->append(it->second);
				result->append("###");
			}
		}
	}
	delete res;
	return result;
}
//parsing select method (life too short to refactor this)
std::vector <std::map <std::string, std::string> > *Database::parseSelect(const std::vector<std::string> &tokens, int start){
	std::vector <std::map <std::string, std::string> > *result = new std::vector <std::map <std::string, std::string> >();
	for (auto it = begin(_tables); it != end(_tables); it++){
		if (it->getName() == tokens[start + 2]){
			std::vector <std::string> where_attributes;
			std::vector <std::string>::const_iterator find = std::find(tokens.begin(), tokens.end(), "WHERE");
			if (find != tokens.end()) where_attributes = split(*(find + 1), ',');
			//parsing where statement
			std::map <std::string, std::string> where_keys;
			std::vector <std::string> find_index;
			for (auto it2 = begin(where_attributes); it2 != end(where_attributes); it2++){
				std::vector <std::string> splitted = split(*it2, '=');
				where_keys[splitted[0]] = splitted[1];
				find_index.push_back(splitted[0]);
			}
			std::map <std::string, std::string> res;
			//linear probing with index
			unsigned long long offset = 0;
			for (auto it2 = begin(_indexes); it2 != end(_indexes); it2++){
				if (it2->getTableName() == it->getName() && it2->attributesCheck(find_index)){
					std::string unhashed;
					for (auto it3 = begin(where_keys); it3 != end(where_keys); it3++){
						unhashed += it3->second;
					}
					unsigned long long h = hash(unhashed);
					offset = it2->getRecOffset(h);
					if (offset == 0) return result;
					for (int i = 0; i < MAX_INDEX_SIZE; i++){
						if (offset == 0){
							h = (h + 1) % MAX_INDEX_SIZE;
							offset = it2->getRecOffset(h);
							continue;
						};
						res = select(*it, offset);
						if (isWhereFound(*it, where_keys, res)) break;
						else{ 
							h = (h + 1) % MAX_INDEX_SIZE;
							offset = it2->getRecOffset(h);
						}
					}
					result->push_back(res);
					return result;
				}
			}
			std::string resStr;
			//select if field not in index, just go through all
			for (auto it2 = begin(_indexes); it2 != end(_indexes); it2++){
				if (it2->getTableName() == it->getName()){
					for (int i = 0; i < MAX_INDEX_SIZE; i++){
						offset = it2->getRecOffset(i);
						if (offset == 0) continue;
						res = select(*it, offset);
						if (isWhereFound(*it, where_keys, res)){
							result->push_back(res);
						}
					}
					break;
				}
			}
			return result;
		}
	}
}
//comparing data to where condition
bool Database::isWhereFound(const Table &table, const std::map <std::string, std::string> &where, 
	std::map <std::string, std::string> &data){
	for (auto it = begin(where); it != end(where); it++){
		//if string, it work like "LIKE"
		if (table.getAttributeType(it->first) == "str"){
			std::string str1;
			std::string str2 = data[it->first];
			std::vector <std::string> spl = split(it->second, '$');
			for (auto it2 = begin(spl); it2 != end(spl); it2++){
				str1.append(*it2);
				if ((it2 + 1) != spl.end()) str1.append(" ");
			}
			std::transform(str1.begin(), str1.end(), str1.begin(), ::tolower);
			std::transform(str2.begin(), str2.end(), str2.begin(), ::tolower);
			if (str2.find(str1) == std::string::npos) return false;
		}else if (it->second != data[it->first]) return false;
	}
	return true;
}
//parsing insert query
bool Database::parseInsert(const std::vector<std::string> &tokens, int start){
	for (auto it = begin(_tables); it != end(_tables); it++){
		if (it->getName() == tokens[start]){
			std::vector <std::string> attributes = split(tokens[start + 1], ',');
			std::string res;
			std::string hash_str;
			std::vector <std::string> index_attrs;
			_file.seekg(0, std::ios::end);
			//find table
			unsigned long long offset = _file.tellg();
			for (auto it2 = begin(_indexes); it2 != end(_indexes); it2++){
				if (it2->getTableName() == tokens[start]){
					index_attrs = it2->getAttributes();
					break;
				}
			}
			//find index and change it
			for (auto it2 = begin(attributes); it2 != end(attributes); it2++){
				std::vector<std::string> params = split(*it2, '=');
				if (!it->hasAttribute(params[0])) return false;
				std::string to = params[1];
			    cutExtend(to, " ", it->getAttributeSize(params[0]));
			    replaceAll(to, '$', ' ');
			    res += to;
			    if (std::find(index_attrs.begin(), index_attrs.end(), params[0]) != index_attrs.end()) hash_str += to;
			}
			res += " ";
			//write new record to file
			writeToFile(res);
			for (auto it2 = begin(_indexes); it2 != end(_indexes); it2++){
				if (it2->getTableName() == tokens[start]){
					it2->update(hash(hash_str), offset);
					break;
				}
			}
			return true;
		}
	}
	return false;
}
//method which accept requests
std::string *Database::request(const std::string &req){
	std::vector<std::string> tokens = split(req, ' ');
	std::string *res = new std::string();
	std::string err = "Error";
	try{
		if (tokens[0] == "CREATE"){
			if (tokens[1] == "INDEX"){
				if (parseCreateIndex(tokens, 2)){
					updateFile();
					err = "Ok";
				}
			}else if (tokens[1] == "TABLE"){
				if (parseCreateTable(tokens, 2)){
					updateFile();
					err = "Ok";
				}
			}
		}else if (tokens[0] == "SELECT"){
			res = parseJoin(tokens, 1);
			if (*res != "Error") err = "Ok";
		}else if (tokens[0] == "INSERT"){
			if (parseInsert(tokens, 2)) err = "Ok";
		}
	}catch(...){

	}
	//logging
	time_t rawtime;
  	struct tm * timeinfo;
  	time(&rawtime);
  	_log << ctime(&rawtime) << req << " ------- " << err << "\n";
	return res;
}