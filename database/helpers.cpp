#include "helpers.h"

//helpers functions

//convert int to string
std::string intToStr(int size, unsigned long long num){
	std::string res = std::to_string(num);
	std::string out;
	for(int i = 0; i < size - res.size(); i++){
		out += "0"; 
	}
	return out + res;
}
//split by delimiter
std::vector<std::string> split(const std::string str, char delim){
	std::vector<std::string> elems;
	std::stringstream ss(str);
    std::string item;
    while (std::getline(ss, item, delim)) {
    	if (item != "") elems.push_back(item);
    }
    return elems;
}
//check is name has only numbers, chars or _
bool isValidName(const std::string &name){
	for (int i = 0; i < name.size(); i++){
		if (!isalnum(name[i]) && name[i] != '_') return false; 
	}
	return true;
}
//is can convert to number
bool isValidNum(const std::string &num){
	try{
		std::stoi(num);
 	}catch (const std::invalid_argument& ia) {
	 	return false;
  	}
  	return true;
}
//get hash of string
unsigned long long hash(const std::string &str){
	unsigned long long h = 0;
	if (str.size() == 0) return h;
	for (int i = 0; i < str.size(); i++){
		h = (31 * h) + str[i];
	}
	return h % MAX_INDEX_SIZE;
}
//remove spaces on the end
std::string trim(std::string& str){
	str.erase(str.find_last_not_of(' ') + 1);         
	return str;
}
//get string with needed size
void cutExtend(std::string &str, const std::string &to, int size){
	if (str.size() < size){
		for (int i = str.size(); i < size; i++){
			str.append(to);
		}
	}else str = str.substr(0, size);
}
//replace all chars in string
void replaceAll(std::string &str, const char from, const char to){
	for (int i = 0; i < str.size(); i++){
		if (str[i] == from) str[i] = to;
	}
}