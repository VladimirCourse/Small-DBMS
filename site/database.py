#!/usr/bin/env python3
import postgresql
import os, re, hashlib
import http.cookies
import socket

#class which works with database
class DataBase:
	def __init__(self, user, passw, port, dbname):
		self.db = postgresql.open(user = user, 
								  password = passw, 
								  port = port, 
								  database = dbname)
	#request as dict
	def req_dict(self, req):
		res = self.db.prepare(req)
		dres = {}
		for i in res:
			dres[tuple(i[j] for j in range(1, len(i)))] = i[0]
		return dres

	#just request
	def req(self, req):
		res = self.db.prepare(req)
		return res()

	#request as set
	def req_set(self, req):
		res = self.db.prepare(req)
		sres = set()
		for i in res:
			sres.add(tuple(i))
		return sres

	def insert_rows(self, table, param, row):
		s = ''
		for i in range(1, param.count(',') + 2):
			s += '$' + str(i) + ','
		query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, param, s[:-1])
		mk = self.db.prepare(query)
		mk.load_rows(row)

	def query(self, req, cond):
		res = self.db.prepare(req)
		return res(*cond)

#connecting to own dbms
class MyDataBase:
	def __init__(self, user, passw, ip, port):
		self.srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srvsock.settimeout(3)
		self.srvsock.connect((ip, port))
#receive response
	def recvall(self):
		data = self.srvsock.recv(4096)
		res = ""
		while data:
			res += data.decode("UTF-8")
			data = self.srvsock.recv(4096)
		return res
#parse string from response 
	def req(self, req):
		self.srvsock.sendall(req.encode())
		res_str = self.recvall()
		self.srvsock.close()
		res = list(tuple())
		for i in res_str.split("###"):
			t = tuple()
			for k in i.split("$$$"):
				if k != "":
					t += (k,)
			if len(t) == 0: continue
			res.append(t)
		return res

#different requests for html page display

def get_keyword_article_count(key_id):
	return request("SELECT COUNT(*) FROM article "
		"JOIN articles_keywords ON id=article_id WHERE keyword_id=%s " % key_id)

def get_keyword_articles(key_id, offset):
	return request("SELECT id,title,type FROM article "
		"JOIN articles_keywords ON id=article_id WHERE keyword_id=%s LIMIT %s 10" % (key_id, offset))

def get_keyword(key_id):
	return request("SELECT * FROM keyword WHERE id=%s" % key_id)

def get_issue_articles_count(issue_id):
	return request("SELECT COUNT(*) FROM article "
		"JOIN articles_issues ON id=article_id WHERE issue_id=%s " % issue_id)

def get_issue_articles(issue_id, offset):
	return request("SELECT id,title,type FROM article "
		"JOIN articles_issues ON id=article_id WHERE issue_id=%s LIMIT %s 10" % (issue_id, offset))

def get_issue(issue_id):
	return request("SELECT * FROM issue WHERE id=%s" % issue_id)

def get_journal_issues(j_id):
	return request("SELECT * FROM issue WHERE journal_id=%s ORDER year " % j_id)

def get_conf_article_count(conf_id):
	return request("SELECT COUNT(*) FROM article "
		"JOIN articles_conferences ON id=article_id WHERE conf_id=%s " % conf_id)

def get_conference_articles(conf_id, offset):
	return request("SELECT id,title,type FROM article "
		"JOIN articles_conferences ON id=article_id WHERE conf_id=%s LIMIT %s 10" % (conf_id, offset))

def get_publisher(pub_id):
	return request("SELECT id,name FROM publisher WHERE id=%s" % pub_id)

def get_conference(conf_id):
	return request("SELECT id,title,issn,isbn,publisher_id FROM conference WHERE id=%s" % conf_id)

def get_author_article_count(auth_id):
	return request("SELECT COUNT(*) FROM article "
		"JOIN articles_authors ON id=article_id WHERE author_id=%s" % auth_id)

def get_author_articles(auth_id, offset):
	return request("SELECT id,title,type FROM article "
		"JOIN articles_authors ON id=article_id WHERE author_id=%s LIMIT %s 10" % (auth_id, offset))

def get_author(auth_id):
	return request("SELECT id,name,institute FROM author WHERE id=%s" % auth_id)

def get_similar_articles(art_id):
	return list(tuple())
	'''
	db = DataBase('postgres', 'postgres', 5433, 'publications')
	return db.req("WITH keys as (SELECT keyword_id FROM articles_keywords WHERE article_id = %s)"
		"SELECT id,title,type FROM article INNER JOIN articles_keywords ON article_id = id "
		"INNER JOIN keys ON articles_keywords.keyword_id = keys.keyword_id "
		"WHERE id != %s GROUP BY id ORDER BY count(*) DESC LIMIT 5 " % (art_id, art_id))'''

def get_article_keywords(art_id):
	return request("SELECT id,title FROM keyword "
		"JOIN articles_keywords ON id=keyword_id WHERE article_id=%s" % art_id)

def get_article_rank(art_id):
	db = DataBase('postgres', 'postgres', 5433, 'publications')
	return db.req("SELECT sum(rate), sum(visit_count) FROM article_rank WHERE article_id = %s" % art_id)

def get_journal(j_id):
	return request("SELECT id,title,issn,publisher_id FROM journal WHERE id=%s" % j_id)

def get_article_issue(art_id):
	return request("SELECT id,issue_ser,journal_id,begin_page,end_page FROM issue "
		"JOIN articles_issues ON id=issue_id WHERE article_id=%s" % art_id)

def get_article_conf(art_id):
	return request("SELECT id,title,begin_page,end_page FROM conference "
		"JOIN articles_conferences ON id=conf_id WHERE article_id=%s" % art_id) 

def get_article_type(art_id):
	return request("SELECT type FROM article WHERE id=%s" % art_id)

def get_article_authors(art_id):
	return request("SELECT id,name FROM author " 
		"JOIN articles_authors ON id=author_id WHERE article_id=%s" % art_id)

def get_article(art_id):
	return request("SELECT id,title,doi,text_url,type FROM article WHERE id=" + art_id)

def get_keywords(params, offset):
	return request("SELECT * FROM keyword %s LIMIT %s 200" % (params, offset))

def get_journals(params, offset):
	return request("SELECT id,title,publisher_id FROM journal %s LIMIT %s 10" % (params, offset))

def get_authors(params, offset):
	return request("SELECT id,name FROM author %s LIMIT %s 10" % (params, offset))

def get_conferences(params, offset):
	return request("SELECT id,title,publisher_id FROM conference %s LIMIT %s 10" % (params, offset))

def get_articles(params, offset):
	return request("SELECT id,title,type FROM article %s LIMIT %s 10" % (params, offset))

def add_article_conf(art_id, conf_id, begin_page, end_page):
	request("INSERT INTO articles_conferences (article_id, conf_id, begin_page, end_page) "
		"VALUES(\'%s\', \'%s\', \'%s\', \'%s\') " % (art_id, conf_id, begin_page, end_page))

def add_article_issue(art_id, issue_id, begin_page, end_page):
	request("INSERT INTO articles_issues (article_id, issue_id, begin_page, end_page) "
		"VALUES(\'%s\', \'%s\', \'%s\', \'%s\') " % (art_id, issue_id, begin_page, end_page))

def add_article_author(art_id, auth_id):
	request("INSERT INTO articles_authors (article_id, author_id) "
		"VALUES(\'%s\', \'%s\') " % (art_id, auth_id))

def add_article(params):
	request("INSERT INTO article (title, doi, text_url, type) "
		"VALUES(\'%s\', \'%s\', \'%s\', \'%s\')" % (params["title"], params["doi"], params["url"], params["type"]))
	return request("SELECT id FROM article "
		"WHERE title = \'%s\' AND doi = \'%s\' AND text_url = \'%s\' AND type = \'%s\'"  % (params["title"], params["doi"], params["url"], params["type"]))[0][0]

def add_author(name):
	req = request("SELECT id FROM author WHERE name = \'%s\'" % name)
	if len(req) == 0:
		request("INSERT INTO author (name) VALUES(\'%s\')" % name)
		req  = request("SELECT id FROM author WHERE name = \'%s\'" % name)
	return req[0][0]
	
def is_issue_exists(issue_id):
	req = request("SELECT id FROM issue WHERE id=%s" % issue_id)
	return len(req) != 0

def is_conf_exists(issue_id):
	req = request("SELECT id FROM conference WHERE id=%s" % issue_id)
	return len(req) != 0

def check_vote(art_id):
	user_id = cookie_user()[0]
	db = DataBase('postgres', 'postgres', 5433, 'publications')

	req = db.req("SELECT rate FROM article_rank WHERE user_id=%s AND article_id=%s" % (user_id, art_id))[0][0]
	return req == 1

def is_rank_exists(art_id, user_id):
	db = DataBase('postgres', 'postgres', 5433, 'publications')
	req = db.req("SELECT * FROM article_rank WHERE user_id=%s AND article_id=%s" % (user_id, art_id))
	return len(req) != 0

def update_article_votes(art_id, vote):
	user_id = cookie_user()[0]
	request("UPDATE article_rank SET rate = %s WHERE user_id = %s "
			"AND article_id = %s" % (vote, user_id, art_id))

def update_article_visits(art_id):
	db = DataBase('postgres', 'postgres', 5433, 'publications')

	user_id = cookie_user()[0]
	if not is_rank_exists(art_id, user_id):
		db.req("INSERT INTO article_rank (user_id, article_id, rate, visit_count) VALUES(%s, %s, 0, 1)" % (user_id, art_id))
	else:
		db.req("UPDATE article_rank SET visit_count = visit_count + 1 WHERE user_id = %s AND article_id = %s" % (user_id, art_id))

def create_user(params):
	params["pass"] = hashlib.md5(params["pass"].encode('utf-8')).hexdigest()
	request("INSERT INTO \"user\" (first_name, last_name, email, password, priveleges) "
		"VALUES(\'%s\', \'%s\', \'%s\', \'%s\', 0)" % (params["first_name"], params["last_name"], params["email"], params["pass"]))

def check_login(params, encr = 1):
	if encr:
		params["pass"] = hashlib.md5(params["pass"].encode('utf-8')).hexdigest()
	req = request("SELECT * FROM user WHERE email=%s,password=%s" % (params["email"], params["pass"]))
	return len(req) != 0

def check_user(email):
	req = request("SELECT id FROM user WHERE email=%s" % email)
	return len(req) != 0

def request(request):
	#db = DataBase('postgres', 'postgres', 5433, 'publications')
	#return db.req(request)
	db = MyDataBase("", "", "127.0.0.1", 30000)
	t = db.req(request)
	return t

#get user params from cookie
def cookie_user():
	cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
	req = request("SELECT id,first_name,last_name,priveleges FROM user WHERE email=%s" % cookie.get("login").value)[0]
	return req
