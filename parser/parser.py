import xml.etree.ElementTree as ET
import re
import time
from bs4 import BeautifulSoup

class Parser:

	def __init__(self, db):
		self.db = db

	#get all data for journal articles parsing
	def fetch_journ(self):
		#data
		self.authors = self.db.req_dict('SELECT id, name FROM author')
		self.keywords = self.db.req_dict('SELECT * FROM keyword')
		self.journals = self.db.req_dict('SELECT id, title, issn FROM journal')
		self.issues = self.db.req_dict('SELECT id, issue_ser, volume, year FROM issue')
		self.articles = self.db.req_dict('SELECT * FROM article')
		self.publishers = self.db.req_dict('SELECT * FROM publisher')
		#offsets which allows to get only last added elements, not all
		self.last_article = self.db.req('SELECT COUNT(*) FROM article')[0][0]
		self.last_author = self.db.req('SELECT COUNT(*) FROM author')[0][0]
		self.last_journal = self.db.req('SELECT COUNT(*) FROM journal')[0][0]
		self.last_pub = self.db.req('SELECT COUNT(*) FROM publisher')[0][0]
		self.last_key = self.db.req('SELECT COUNT(*) FROM keyword')[0][0]
		self.last_issue = self.db.req('SELECT COUNT(*) FROM issue')[0][0]

	#get all data for conference articles parsing
	def fetch_conf(self):
		#data
		self.authors = self.db.req_dict('SELECT id, name FROM author')
		self.keywords = self.db.req_dict('SELECT * FROM keyword')
		self.confs = self.db.req_dict('SELECT id, title, issn, isbn FROM conference')
		self.articles = self.db.req_dict('SELECT * FROM article')
		self.publishers = self.db.req_dict('SELECT * FROM publisher')
		#offsets which allows to get only last added elements, not all
		self.last_article = self.db.req('SELECT COUNT(*) FROM article')[0][0]
		self.last_author = self.db.req('SELECT COUNT(*) FROM author')[0][0]
		self.last_conf = self.db.req('SELECT COUNT(*) FROM conference')[0][0]
		self.last_pub = self.db.req('SELECT COUNT(*) FROM publisher')[0][0]
		self.last_key = self.db.req('SELECT COUNT(*) FROM keyword')[0][0]

	#add row
	def add_row(self, row, row_set, row_list):
		if row not in row_set:
			row_set[row] = 0
			row_list.append(row)
	#create relation
	def create_rel(self, row, from_ins, row_set, row_list, relation):
		for i in from_ins:
			to_ins = (i,)
			self.add_row(to_ins, row_set, row_list)
			relation[row].add(to_ins)
	#insert relation to res
	def insert_relations(self, relation, first, second):
		res = []
		for i in relation:
			first_id = first[i]
			for k in relation[i]:
				second_id = second[k]
				res.append((first_id, second_id,))
		return res
	#init dictionary, some fields can be empty
	def init_dict(self):
		res = {}
		res['doi'] = ['']
		res['thesaurusterms'] = []
		res['issn'] = ['']
		res['isbn'] = ['']
		res['spage'] = ['']
		res['epage'] = ['']
		res['issue'] = ['']
		res['volume'] = ['']
		res['py'] = ['']
		return res
	#parse authors
	def parse_authors(self, authors_raw):
		formed_authors = []
		for i in authors_raw.split(';'):
			formed_authors.append(i.strip())
		return formed_authors
	#remove html tages
	def remove_tags(self, to_remove):
		soup = BeautifulSoup(to_remove)
		res = ''.join(soup.findAll(text=True))
		return res

	#insert methods to databse

	def insert_articles(self, articles_to):
		self.db.insert_rows(
				"INSERT INTO article (title,doi,text_url,type) VALUES ($1, $2, $3, $4)",
				articles_to
			)
		off = self.last_article
		articles_keys = self.db.req_dict(
				"SELECT * FROM article ORDER BY id ASC OFFSET %s" % off
			)
		#recalculate offset
		self.last_article += len(articles_to)
		self.articles.update(articles_keys)

	def insert_authors(self, authors_to):
		self.db.insert_rows(
				"INSERT INTO author (name) VALUES ($1)",
				authors_to
			)
		off = self.last_author
		authors_keys = self.db.req_dict(
				"SELECT id, name FROM author ORDER BY id ASC OFFSET %s" % off
			)		
		self.last_author += len(authors_to)
		self.authors.update(authors_keys)

	def insert_keywords(self, keywords_to):
		self.db.insert_rows(
				"INSERT INTO keyword (title) VALUES ($1)",
				keywords_to
			)
		off = self.last_key
		keyword_keys = self.db.req_dict(
				"SELECT * FROM keyword ORDER BY id ASC OFFSET %s" % off
			)
		self.last_key += len(keywords_to)
		self.keywords.update(keyword_keys)

	def insert_confs(self, confs_to):
		self.db.insert_rows(
				"INSERT INTO conference (title,issn,isbn,publisher_id) VALUES ($1,$2,$3,$4)",
				confs_to
			)
		off = self.last_conf 
		confs_keys = self.db.req_dict(
				"SELECT id,title,issn,isbn FROM conference ORDER BY id ASC OFFSET %s" % off
			)
		self.last_conf += len(confs_to)
		self.confs.update(confs_keys)

	def insert_journals(self, journ_to):
		self.db.insert_rows(
				"INSERT INTO journal (title,issn,publisher_id) VALUES ($1,$2,$3)",
				journ_to
			)
		off = self.last_journal 
		journs_keys = self.db.req_dict(
				"SELECT id,title,issn FROM journal ORDER BY id ASC OFFSET %s" % off
			)
		self.last_journal += len(journ_to)
		self.journals.update(journs_keys)

	def insert_issues(self, issue_to):
		self.db.insert_rows(
				"INSERT INTO issue (journal_id,issue_ser,volume, year) VALUES ($1,$2,$3,$4)",
				issue_to
			)
		off = self.last_issue
		issue_keys = self.db.req_dict(
				"SELECT id,issue_ser,volume,year FROM issue ORDER BY id ASC OFFSET %s" % off
			)
		self.last_issue += len(issue_to)
		self.issues.update(issue_keys)

	def insert_pubs(self, pubs_to):
		self.db.insert_rows(
				"INSERT INTO publisher (name) VALUES ($1)",
				pubs_to
			)
		off = self.last_pub
		pub_keys = self.db.req_dict(
				"SELECT * FROM publisher ORDER BY id ASC OFFSET %s" % off
			)
		self.last_pub += len(pubs_to)
		self.publishers.update(pub_keys)

	#main method for parsing journal article
	def parse_journ_article(self, text):
		#to insert
		articles_to = []
		authors_to = []
		keywords_to = []
		jounrs_to = []
		issues_to = []
		publishers_to = []
		#relations
		articles_authors = {}
		articles_keywords = {}
		articles_issues = {}
		journ_pubs = {}
		issue_journs = {}
		#xml tree
		tree = ET.ElementTree(ET.fromstring(text))

		for i in tree.iter('document'):
			res = self.init_dict()
			for k in i.iter():
				res[k.tag] = [j.text for j in k.iter()]
			
			soup = BeautifulSoup(res['title'][0])
			title = ''.join(soup.findAll(text=True))
			#row which will be inserted
			to_insert = (title, res['doi'][0], res['pdf'][0], 0)
			
			articles_authors[to_insert] = set()
			articles_keywords[to_insert] = set()
			articles_issues[to_insert] = set()
			#if article not in database
			if to_insert not in self.articles:
				self.articles[to_insert] = 0
				articles_to.append(to_insert)
				authors_raw = res['authors'][0]
				#parse authors and create relation 
				if authors_raw:
					formed_authors = self.parse_authors(authors_raw)
					self.create_rel(to_insert, formed_authors, self.authors, authors_to, articles_authors)
				#keywords
				terms = res['thesaurusterms']
				if terms:
					self.create_rel(to_insert, terms[1:], self.keywords, keywords_to, articles_keywords)

			title = self.remove_tags(res['pubtitle'][0])
			#create relations, get publisher, journal and issue
			journ_to = (title,res['issn'][0],)
			issue_to = (res['issue'][0],res['volume'][0],int(res['py'][0]),) 
			self.add_row(journ_to, self.journals, jounrs_to)
			self.add_row((res['publisher'][0],), self.publishers, publishers_to)
			self.add_row(issue_to, self.issues, issues_to)
			articles_issues[to_insert].add(issue_to + (res['spage'][0], res['epage'][0],))
			journ_pubs[journ_to] = res['publisher'][0]
			issue_journs[issue_to] = journ_to
		#insert parsed
		self.insert_articles(articles_to)
		self.insert_authors(authors_to)
		self.insert_keywords(keywords_to)
		self.insert_pubs(publishers_to)
		#insert journals
		journ_to_insert = []
		for i in jounrs_to:
			pub = journ_pubs[i] 
			pub_id = self.publishers[(pub,)]
			journ_to_insert.append(i + (pub_id,))
		self.insert_journals(journ_to_insert)
		#insert issues
		issues_to_insert = []
		for i in issues_to:
			journal = issue_journs[i] 
			j_id = self.journals[(journal)]
			issues_to_insert.append((j_id,) + i)

		self.insert_issues(issues_to_insert)
		#insert article to author relation
		auth_rel = self.insert_relations(articles_authors, self.articles, self.authors)
		self.db.insert_rows(
					"INSERT INTO articles_authors (article_id, author_id) VALUES ($1,$2)",
					auth_rel
			)
	
		#insert article to keyword relation
		keyw_rel = self.insert_relations(articles_keywords, self.articles, self.keywords)

		self.db.insert_rows(
					"INSERT INTO articles_keywords (article_id, keyword_id) VALUES ($1,$2)",
					keyw_rel
			)
	
		article_issues_get = self.db.req_set('SELECT issue_id, article_id, begin_page, end_page FROM articles_issues')
		#insert article to issue relation
		relations_to = []
		for i in articles_issues:
			art_id = self.articles[i]
			for k in articles_issues[i]:
				issue_id = self.issues[k[:3]]
				rel_to = (issue_id, art_id,) + k[3:]
				if rel_to not in article_issues_get:
					relations_to.append(rel_to)


		self.db.insert_rows(
					"INSERT INTO articles_issues (issue_id, article_id, begin_page, end_page) VALUES ($1,$2,$3,$4)",
					relations_to
			)
	

	def parse_conf_article(self, text):
		#what will be inserted
		articles_to = []
		authors_to = []
		keywords_to = []
		confs_to = []
		publishers_to = []
		#relations
		articles_authors = {}
		articles_keywords = {}
		articles_confs = {}
		confs_pubs = {}
		#xml tree
		tree = ET.ElementTree(ET.fromstring(text))
		#parsin xml tree
		for i in tree.iter('document'):
			res = self.init_dict()
			for k in i.iter():
				res[k.tag] = [j.text for j in k.iter()]
			
			soup = BeautifulSoup(res['title'][0])
			title = ''.join(soup.findAll(text=True))

			to_insert = (title, res['doi'][0], res['pdf'][0], 1)
			
			articles_authors[to_insert] = set()
			articles_keywords[to_insert] = set()
			articles_confs[to_insert] = set()
			#if article not in database
			if to_insert not in self.articles:
				self.articles[to_insert] = 0
				articles_to.append(to_insert)
				#authors
				authors_raw = res['authors'][0]
				if authors_raw:
					formed_authors = self.parse_authors(authors_raw)
					self.create_rel(to_insert, formed_authors, self.authors, authors_to, articles_authors)
				#keywords
				terms = res['thesaurusterms']
				if terms:
					self.create_rel(to_insert, terms[1:], self.keywords, keywords_to, articles_keywords)

			title = self.remove_tags(res['pubtitle'][0])
			#parse relations and other
			conf_to = (title,res['issn'][0],res['isbn'][0],)
			self.add_row(conf_to, self.confs, confs_to)
			self.add_row((res['publisher'][0],), self.publishers, publishers_to)
			articles_confs[to_insert].add(conf_to + (res['spage'][0], res['epage'][0],))
			confs_pubs[conf_to] = res['publisher'][0]
		#insert to databse
		self.insert_articles(articles_to)
		self.insert_authors(authors_to)
		self.insert_keywords(keywords_to)
		self.insert_pubs(publishers_to)
		#insert conferences
		conf_to_insert = []
		for i in confs_to:
			pub = confs_pubs[i] 
			pub_id = self.publishers[(pub,)]
			conf_to_insert.append(i + (pub_id,))

		self.insert_confs(conf_to_insert)
		#insert author to article relation
		auth_rel = self.insert_relations(articles_authors, self.articles, self.authors)
		self.db.insert_rows(
					"INSERT INTO articles_authors (article_id, author_id) VALUES ($1,$2)",
					auth_rel
			)
	
		#insert keyword to article relation
		keyw_rel = self.insert_relations(articles_keywords, self.articles, self.keywords)
		self.db.insert_rows(
					"INSERT INTO articles_keywords (article_id, keyword_id) VALUES ($1,$2)",
					keyw_rel
			)
	
		article_confs_get = self.db.req_set('SELECT conf_id, article_id, begin_page, end_page FROM articles_conferences')
		#insert article to conference relation
		relations_to = []
		for i in articles_confs:
			art_id = self.articles[i]
			for k in articles_confs[i]:
				conf_id = self.confs[k[:3]]
				rel_to = (conf_id, art_id,) + k[3:]
				if rel_to not in article_confs_get:
					relations_to.append(rel_to)


		self.db.insert_rows(
					"INSERT INTO articles_conferences (conf_id, article_id, begin_page, end_page) VALUES ($1,$2,$3,$4)",
					relations_to
			)
	
