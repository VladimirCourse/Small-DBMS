#pragma once

#include <stdio.h>
#include <iostream>
#include <map>
#include <sstream>
#include <vector>
#include <algorithm>

const int MAX_INDEX_SIZE = 10000;

enum Type{integer, varchar};

std::string intToStr(int size, unsigned long long num);
std::vector<std::string> split(const std::string str, char delimiter);
bool isValidName(const std::string &name);
bool isValidNum(const std::string &num);
unsigned long long hash(const std::string &str);
std::string trim(std::string &str);
void cutExtend(std::string &str, const std::string &to, int size);
void replaceAll(std::string &str, const char from, const char to);