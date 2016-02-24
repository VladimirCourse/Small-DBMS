from database import *
import http.cookies
import os, re, hashlib

#file with help functions

#gets parameters from previous page from cgi field storage
def get_storage_params(storage):
	params = {}
	param_str = ""
	for i in storage.keys():
		if i == "page": continue
		params[i] = storage.getfirst(i)
		param_str += "&" + i + "=" + params[i]
	return (params, param_str)

#calculate offset and range for paginaton
def calculate_offset(offset, size = 10):
	p_range = 1
	if offset == None:
		offset = 0
	else:
		p_range = int(offset)
		offset = (int(offset) - 1) * size
	return (p_range, offset,)

#email validation
def check_email_input(email):
	return re.match(r'^[0-9a-z]+@[0-9a-z]+\.[0-9a-z]+$', email) != None

#name validation
def check_name_input(name):
	return re.match(r'^[A-Za-z]+$', name) != None

#pass validation
def check_pass_input(passw):
	return len(passw) > 5

#setting cookies
def set_cookie(params):
	cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
	login = cookie.get("login")
	passw = cookie.get("pass")
	cookie = http.cookies.SimpleCookie()
	cookie["login"] = params["email"]
	cookie["pass"] = params["pass"]	
	print(cookie)

#check existiting cookies, then checking is it valid for authorization
def check_cookie():
	cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
	login = cookie.get("login")
	passw = cookie.get("pass")
	if login is None or passw is None:
		return 0
	else:
		params = {}
		params["email"] = login.value
		params["pass"] = passw.value
		return check_login(params, 0)

#parse search author, keyword or etc
def parse_search(params, field):
	query = ""
	if "search" in params:
		query += "WHERE "
		query += field + "=" + magic_query_function(params["search"])
	query += " ORDER "
	if "order_type" in params:
		query += field + " "
		query += params["order_type"] + " "
	else:
		query += field + " asc "
	return query

#parse search article
def parse_search_article(params):
	query = ""
	prev = 0
	if "search" in params:
		query += "WHERE "
		query += "title=" + magic_query_function(params["search"])
		prev = 1
	if "type" in params:
		if prev == 1:
			query += ","
		else:
			query += "WHERE "
		query += "type=" + params["type"]

	query += " ORDER "
	if "order" in params:
		query += params["order"] + " "
	else:
		query += "title "
	if "order_type" in params:
		query += params["order_type"] + " "
	return query
	
def magic_query_function(query):
	return query.replace(" ", "$")