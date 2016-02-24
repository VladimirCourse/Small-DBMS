from database import *
from helpers import *
import http.cookies
import os, re, hashlib

#functions which printing parts of html page

#ok alert
def print_ok(ok):
	print('''<div class="row">
 		<div align = "center" class="col-md-4"></div>
 		<div align = "center" class="col-md-4">
 		''')
	print("<div class=\"alert alert-success\">")
	print("<b>%s</b>" % ok)
	print("</div></div></div>")

#error alert
def print_alert(alert):
	print('''<div class="row">
 		<div align = "center" class="col-md-4"></div>
 		<div align = "center" class="col-md-4">
 		''')
	print("<div class=\"alert alert-danger\">")
	print("<b>%s</b>" % alert)
	print("</div></div></div>")

#header of authorized or not authorized user, if user is logged in, then he can logout or add new article
def print_header(logged):
	if logged:
		print("<ul class=\"nav navbar-nav pull-right\">"
			  "<li><a style=\"pointer-events: none;cursor: default;\">Logged as <b>%s </b></a></li>" % (cookie_user()[1] + " " + cookie_user()[2]))
		if cookie_user()[3] == 1:
			print("<li><a href=\"/add_article\">Add article</a></li>")
		print("<li><a href=\"/logout\">Logout</a></li></ul></div>")
	else:
		print(''' <ul class="nav navbar-nav pull-right">
              <li><a href="/login">Login</a></li>
              <li><a href="/register">Register</a></li>
            </ul></div>''')

#print list of references
def print_ref_list(ref_list, title, ref):
	if len(ref_list) != 0:
		print("<br>")
		print("<b>%s: </b>" % title)
		c = 0
		for k in ref_list:
			print(ref % k)
			if c == len(ref_list) - 1: 
				print("...")
				break
			else: print( ",&nbsp&nbsp")
			c += 1

#print list of keywords
def print_keyword_list(req):
	for i in req:
		print("<b><a href=\"/keyword?id=%s\"> <font color =\"#853C16\">%s</font></a>, </b>" % (i[0], i[1]))

#print parts of pages

def print_keyword_articles(key_id, offset):
	keyword = get_keyword(key_id)[0]
	print("<div class=\"article\" >")
	print("<b><font color=\"#853C16\">%s</font></b>" % keyword[1])
	print("<br><br>")
	print("<b>Articles: </b>")	
	print("<div class=\"article\">")
	articles = get_keyword_articles(key_id, offset)
	print_article_list(articles)
	print("</div>")

def print_issue_articles(issue_id, offset):
	print("<div class=\"article\">")
	articles = get_issue_articles(issue_id, offset)
	print_article_list(articles)
	print("</div>")

def print_issue_info(issue_id):
	issue = get_issue(issue_id)[0]
	print("<div class=\"article\" >")
	print("<b><font color=\"#853C16\">Issue %s</font></b>" % issue[2])
	journal = get_journal(issue[1])[0]
	print("<br>")
	print("<b>Journal: </b>")
	print("<a href = /journal?id=%s><font color=\"#853C16\">%s</font></a>" % (journal[0], journal[1]))
	if issue[3] != None:
		print("<br><b>Volume: </b> %s" % issue[3])
	if issue[4] != None:
		print("<br><b>Year: </b> %s" % issue[4])
	print("<br><br>")

def print_journal_issues(j_id):
	print("<div class=\"article\">")
	issues = get_journal_issues(j_id)
	print_issue_list(issues)
	print("</div>")

def print_journal_info(j_id):
	journal = get_journal(j_id)[0]
	print("<div class=\"article\" >")
	print("<b><font color=\"#853C16\">%s</font></b>" % journal[1])
	if journal[2] != None:
		print("<br><b>Issn: </b> %s" % journal[2])
	publisher = get_publisher(journal[3])[0]
	print("<br><b>Publisher: </b>")
	print("<b><font color=\"#853C16\">%s</font></b>" % publisher[1])

def print_conference_articles(conf_id, offset):
	print("<b>Articles: </b>")	
	print("<div class=\"article\">")
	conf = get_conference_articles(conf_id, offset)
	print_article_list(conf)
	print("</div>")

def print_conference_info(conf_id):
	conference = get_conference(conf_id)[0]
	print("<div class=\"article\" >")
	print("<b><font color=\"#853C16\">%s</font></b>" % conference[1])
	if len(conference[2]) != 0:
		print("<br><b>Issn: </b> %s" % conference[2])
	if len(conference[2]) != 0:
		print("<br><b>Isbn: </b> %s" % conference[3])
	publisher = get_publisher(conference[4])[0]
	print("<br><b>Publisher: </b>")
	print("<b><font color=\"#853C16\">%s</font></b>" % publisher[1])
	print("<br><br>")

def print_author_articles(auth_id, offset):
	print("<b>Articles: </b>")
	print("<div class=\"article\">")
	articles = get_author_articles(auth_id, offset)
	print_article_list(articles)
	print("</div>")
	return get_author_article_count(auth_id)[0][0]

def print_author_info(auth_id):
	author = get_author(auth_id)[0]
	print("<div class=\"article\" >")
	print("<b><font color=\"#853C16\">%s</font></b>" % author[1])
	if author[2] != None:
		print("<br><b>Institution: </b> %s" % author[2])
	print("<br><br>")

def print_similar_articles(art_id):
	similar = get_similar_articles(art_id)
	print("<br>")
	if len(similar) != 0:
		print("<b>Similar articles: </b>")
		print("<br><br>")
		print_article_list(similar)
	print("</div>")	

def print_article_keywords(art_id):
	keys = get_article_keywords(art_id)
	if len(keys) != 0:
		print("<br>")
		print("<b>Keywords: </b>")
		for k in keys:
			print("<a href = /keyword?id=%s><font color=\"#853C16\">%s</font></a>" % k + ",")
	print("<br>")

def print_article_rate(art_id, is_logged):
	rank = get_article_rank(art_id)[0]
	rank_num = 0
	visit_count = 0
	if rank[0] != None: rank_num = rank[0]
	if rank[1] != None: visit_count = rank[1]
	print("<br><b>Rank: </b> %s" % rank_num)
	if is_logged:
		if check_vote(art_id):
			print("<a href =/vote?id=%s&vote=0><font color=\"#853C16\">Unvote</font></a>" % art_id)
		else:
			print("<a href =/vote?id=%s&vote=1><font color=\"#853C16\">Vote</font></a>" % art_id)
	print("<br><b>Visit count: </b> %s" % visit_count)

def print_article_journal(art_id):
	issue = get_article_issue(art_id)[0]
	journal = get_journal(issue[2])[0]
	print("<br>")
	print("<b>Journal: </b>")
	print("<a href = /journal?id=%s><font color=\"#853C16\">%s</font></a>" % (journal[0], journal[1]))
	print("<br>")
	print("<b>Issue: </b>")
	print("<a href = /issue?id=%s><font color=\"#853C16\">%s</font></a>" % (issue[0], issue[1]))
	print("<br><b>Pages: </b> from")
	print("%s to %s" % (issue[3], issue[4]))

def print_article_conf(art_id):
	print("<br>")
	print("<b>Conference: </b>")
	conf = get_article_conf(art_id)[0]
	print("<a href = /conference?id=%s><font color=\"#853C16\">%s</font></a>" % (conf[0], conf[1]) + ",")
	print("<br><b>Pages: </b> from")
	print("%s to %s" % (conf[2], conf[3]))

def print_article_authors(art_id):
	authors = get_article_authors(art_id)
	if len(authors) != 0:
		print("<br>")
		print("<b>Auhtors: </b>")
		for k in authors:
			print("<a href = /author?id=%s><font color=\"#853C16\">%s</font></a>" % k + ",&nbsp&nbsp")

def print_article_info(art_id):
	article = get_article(art_id)[0]
	print("<div class=\"article-head\" >")
	print("<b><font color=\"#853C16\">%s</font></b>" % article[1])
	print("</div>")
	print("<br><b>DOI: </b>" + article[2])
	print("<br><b>URL: </b><a href = \"%s\"> <font color=\"#853C16\">%s</font></a>" % (article[3], article[3]))

def print_content_keywords(params, offset):
	print("<div class=\"article\">")
	keywords = get_keywords(parse_search(params, "title"), offset)
	print_keyword_list(keywords)
	print("</div>")
	return len(keywords)

def print_content_journals(params, offset):
	print("<div class=\"article\">")
	journals = get_journals(parse_search(params, "title"), offset)
	print_journal_list(journals)
	print("</div>")
	return len(journals)

def print_content_conferences(params, offset):
	print("<div class=\"article\">")
	conferences = get_conferences(parse_search(params, "title"), offset)
	print_conference_list(conferences)
	print("</div>")
	return len(conferences)

def print_content_authors(params, offset):
	print("<div class=\"article\">")
	authors = get_authors(parse_search(params, "name"), offset)
	print_author_list(authors)
	print("</div>")
	return len(authors)

def print_content_articles(params, offset):
	print("<div class=\"article\">")
	articles = get_articles(parse_search_article(params), offset)
	print_article_list(articles)
	print("</div>")
	return len(articles)


def print_journal_list(req):
	for i in req:
		print("<div class=\"article\" >")
		print("<b><a href=\"/journal?id=%s\"> <font color=\"#853C16\">%s</font></a></b>" % (i[0], i[1]))
		publisher = request("SELECT id,name FROM publisher WHERE id=" + str(i[2]))[0]
		print("<br>Publisher: ")
		print("<b><font color=\"#853C16\">%s</font></b>" % publisher[1])
		print("<hr></div>")

#print list of issues
def print_issue_list(req):
	prev_year = 0
	cur_year = 1
	for i in req:
		cur_year = i[4]
		if cur_year != prev_year:
			print("<br>")
			prev_year = cur_year
			print("<b>Year: </b> %s, <b>Issues: </b>" % cur_year)
		print("<b><a href=\"/issue?id=%s\"> <font color=\"#853C16\">%s</font></a></b>" % (i[0], i[2]))


def print_conference_list(req):
	for i in req:
		print("<div class=\"article\" >")
		print("<b><a href=\"/conference?id=%s\"> <font color=\"#853C16\">%s</font></a></b>" % (i[0], i[1]))
		publisher = request("SELECT id,name FROM publisher WHERE id=" + str(i[2]))[0]
		print("<br>Publisher: ")
		print("<b><font color=\"#853C16\">%s</font></b>" % publisher[1])
		print("<hr></div>")

def print_author_list(req):
	for i in req:
		print("<div class=\"article\" >")
		print("<b><a href=\"/author?id=%s\"> <font color=\"#853C16\">%s</font></a></b>" % (i[0], i[1]))
		articles = request("SELECT id,title FROM article " 
					"JOIN articles_authors ON id=article_id WHERE author_id=%s LIMIT 0 3" % i[0])
		print_ref_list(articles, "Articles", "<a href = /article?id=%s><font color=\"#853C16\">%s</font></a>")
	
		print("<hr></div>")

def print_article_list(req):
	for i in req:
		print("<div>")
		print("<b><a href=\"/article?id=%s\"> <font color=\"#853C16\">%s</font></a></b>" % (i[0], i[1]))
		authors = request("SELECT id,name FROM author " 
					"JOIN articles_authors ON id=author_id WHERE article_id=%s LIMIT 0 3" % i[0])
		print_ref_list(authors, "Authors", "<a href = /author?id=%s><font color=\"#853C16\">%s</font></a>")
	
		keys = request("SELECT id,title FROM keyword "
			"JOIN articles_keywords ON id=keyword_id WHERE article_id=%s LIMIT 0 3" % i[0])
		
		print_ref_list(keys, "Keywords", "<a href = /keyword?id=%s><font color=\"#853C16\">%s</font></a>")
		print("<br>")
		if i[2] == "1" or i[2] == "No data":
			print("<b>Conference: </b>")
			conf = request("SELECT id,title FROM conference "
				"JOIN articles_conferences ON id=conf_id WHERE article_id=" + str(i[0]))[0]
			print("<a href = /conference?id=%s><font color=\"#853C16\">%s</font></a>" % (conf[0], conf[1]))
		else:
			issue = request("SELECT id,issue_ser,journal_id FROM issue "
				"JOIN articles_issues ON id=issue_id WHERE article_id=" + str(i[0]))[0]
			journal = request("SELECT id,title FROM journal WHERE id=" + str(issue[2]))[0]
			print("<b>Journal: </b>")
			print("<a href = /journal?id=%s><font color=\"#853C16\">%s</font></a>" % (journal[0], journal[1]))
			print("<br>")
			print("<b>Issue: </b>")
			print("<a href = /issue?id=%s><font color=\"#853C16\">%s</font></a>" % (issue[0], issue[1]))
		print("<hr></div>")	

#print search left part
def print_search(page):
	print(''' <div class="col-md-3 left-sidebar">
  <form name="search" action="%s" method="get" class="form-inline form-search pull-left searcher">
    <div class="input-group">
      <label class="sr-only" for="searchInput">Search</label>
      <input class="form-control" id="searchInput" type="text" name="search"  placeholder="Search">
      <div class="input-group-btn">
        <button type="submit" class="btn btn-primary search-btn">Search</button>
      </div>
    </div>
    <hr>
    <div align="center"> 
      Ordering
    </div>
     <br>
    <div class="radio search-chbox">
      <label><input name = "order_type" type="radio" value="asc">
      Ascending
      </label>
    </div>
    <br>
    <div class="radio search-chbox">
      <label><input name = "order_type" type="radio" value="desc">
      Descending
      </label>
    </div>
    <br>
    <hr>
</div>
<div class="col-md-9 content">''' % page)

#footer of page
def print_footer():
	print("</div></div></div></body></html>")

#print search left part for articles
def print_articles_search():
	print(''' <div class="col-md-3 left-sidebar">
  <form name="search" action="articles" method="get" class="form-inline form-search pull-left searcher">
    <div class="input-group">
      <label class="sr-only" for="searchInput">Search</label>
      <input class="form-control" id="searchInput" type="text" name="search"  placeholder="Search">
      <div class="input-group-btn">
        <button type="submit" class="search-btn btn ">Search</button>
      </div>
    </div>
    <hr>
    <div align="center">
      Type of publication
    </div>
    <br>
    <div class="radio search-chbox">
      <label><input checked name = "type" type="radio" value="">
      Any
      </label>
    </div>
    <br>
    <div class="radio search-chbox">
      <label><input name = "type" type="radio" value="1">
      Conference
      </label>
    </div>
    <br>
    <div class="radio search-chbox">
      <label><input name = "type" type="radio" value="0">
      Journal
      </label>
    </div>
    <hr>
     <div align="center"> 
      Ordering
    </div>
     <br>
    <div class="radio search-chbox">
      <label><input name = "order_type" type="radio" value="asc">
      Ascending
      </label>
    </div>
    <br>
    <div class="radio search-chbox">
      <label><input name = "order_type" type="radio" value="desc">
      Descending
      </label>
    </div>
    <br>
    <hr>
</div>
<div class="col-md-9 content">
''')

def print_head():
	print('''<!DOCTYPE html>
		<html lang="en">
		<head>
		  <meta charset="utf-8">
		  <meta http-equiv="X-UA-Compatible" content="IE=edge">
		  <meta name="viewport" content="width=device-width, initial-scale=1">
		  <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
		  <title></title>

		  <!-- Bootstrap -->
		  <link href="css/bootstrap.min.css" rel="stylesheet">
		  <link href="css/additional.css" rel="stylesheet">
		  <!--		  <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
		  <script src="//code.jquery.com/jquery-1.10.2.js"></script>
		  <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>
		  <script src="http://code.jquery.com/jquery-git2.js"></script> -->
		  <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
		  <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
		    <!--[if lt IE 9]>
		      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
		      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
		      <![endif]-->

		    </head>
		    <body>
		    <div class="container">
		      <div class="row"> 
		        <div class="col-md-12 head-block">
		        </div>
		          <div class="col-md-12 top-menu">
		            <ul class="nav navbar-nav">
		              <li><a href="/articles">Articles</a></li>
		              <li><a href="/authors">Authors</a></li>
		              <li><a href="/conferences">Conferences</a></li>
		              <li><a href="/journals">Journals</a></li>
		              <li><a href="/keywords">Keywords</a></li>
		            </ul>''')

#print paginator
def print_single_paginator(page, count, param_str, p_range):
	begin = max(p_range - 2, 1)
	end = max(begin + 5, 6)
	end = min(end, count // 10 + 1)
	if count <= 10: end = 2
	#go left
	print(
			"<div align=center>"
			"<ul class = \"pagination pages\">"
			 "<li>"
			  "<a href=\"/%s?page=%s%s\"  aria-label=\"Previous\">" % (page, max(p_range - 1, 1), param_str) +
				"<span aria-hidden=\"true\">&laquo;</span>"
			 "</a>"
			"</li>")
	#go direct page
	for i in range(begin, end):
		if i == p_range:
			print("<li class = \"active\"><a href=\"/%s?page=%s%s\">%s</a></li>" % (page, i, param_str, i))
		else:
			print("<li><a href=\"/%s?page=%s%s\">%s</a></li>" % (page, i, param_str, i))
	#go right
	print("<li>"
			  "<a href=\"/%s?page=%s%s\" aria-label=\"Next\">" % (page, min(p_range + 1, end - 1), param_str) +
				"<span aria-hidden=\"true\">&raquo;</span>"
			 "</a>"
			"</li>"
			  "</ul>"
			 "</div>")

#paginator
def print_paginator(page, count, param_str, p_range, size=10):
	begin = max(p_range - 2, 1)
	end = max(begin + 5, 6)
	if count == 0:
		print("<div align=center>No matches!</div>")
	elif count == size:
		#go left
		print(
			"<div align=center>"
			"<ul class = \"pagination pages\">"
			"<li>"
			"<a href=\"/%s?page=%s%s\"  aria-label=\"Previous\">" % (page, max(p_range - 1, 1), param_str) +
			"<span aria-hidden=\"true\">&laquo;</span>"
			"</a>"
			"</li>")
		#go to direct page
		for i in range(begin, end):
			if i == p_range:
				print("<li class = \"active\"><a href=\"/%s?page=%s%s\">%s</a></li>" % (page, i, param_str, i))
			else:
				print("<li><a href=\"/%s?page=%s%s\">%s</a></li>" % (page, i, param_str, i))
		#go right
		print("<li>"
					"<a href=\"/%s?page=%s%s\" aria-label=\"Next\">" % (page, p_range + 1, param_str) +
					"<span aria-hidden=\"true\">&raquo;</span>"
					"</a>"
					"</li>"
					"</ul>"
					"</div>")
#pring registration, login etc forms

def print_reg():
	print(''' <div class="form-group">
 	<div class="row">
 		<h3 align="center"> Registration </h3>
 		<div align = "center" class="col-md-4"></div>
 		<div align = "center" class="col-md-4">
 			<form action="check_register" method="post" class="form-horizontal">
 				<div class="control-group">
 					<label for="first_name" class="control-label pull-left">First name</label>
 					<input type="text" name="first_name" class="form-control" placeholder="Enter first name"/>
 					<br>
 					<label for="last_name" class="control-label pull-left">Last name</label>
 					<input type="text" name="last_name" class="form-control" placeholder="Enter last name"/>
 					<br>
 					<label for="email" class="control-label pull-left">Email</label>
 					<input type="text" name="email" class="form-control" placeholder="Enter email"/>
 					<br>
 					<label for="pass" class="control-label pull-left">Password</label>
 					<input type="password" name="pass" class="form-control" placeholder="Enter email"/>
 					<br>
 					<button type="submit" class="btn-success btn reg-btn search-btn" >Register</button>  
 				</div>
 			</form>
 		</div>
 	</div>
''')

def print_login():
	print(''' <div class="form-group">
 	<div class="row">
 		<div align = "center" class="col-md-4"></div>
 		<div align = "center" class="col-md-4">
 			<h3>Login </h3>
 			<form action="check_login" method="post" class="form-horizontal">
 				<div class="control-group">
 					<label for="email" class="control-label pull-left">Email</label>
 					<input type="text" name="email" class="form-control" placeholder="Enter email"/>
 					<br>
 					<label for="pass" class="control-label pull-left">Password</label>
 					<input type="password" name="pass" class="form-control" placeholder="Enter email"/>
 					<br>
 					<button type="submit" class="btn-success btn reg-btn search-btn" >Login</button>  
 				</div>
 			</form>
 		</div>
 	</div>
''')

def print_add_article():
	print(''' <div class="form-group">
	 	<div class="row">
	 		<h3 align="center"> Add article </h3>
	 		<div align = "center" class="col-md-4"></div>
	 		<div align = "center" class="col-md-4">
	 			<form action="check_article_add" method="post" class="form-horizontal">
	 				<div class="control-group">
	 					<label for="title" class="control-label pull-left">Title</label>
	 					<input type="text" name="title" class="form-control" placeholder="Enter title"/>
	 					<br>
	 					<label for="doi" class="control-label pull-left">DOI</label>
	 					<input type="text" name="doi" class="form-control" placeholder="Enter DOI"/>
	 					<br>
	 					<label for="url" class="control-label pull-left">URL</label>
	 					<input type="text" name="url" class="form-control" placeholder="Enter URL"/>
	 					<br>
	 					<div class="radio search-chbox" style="float:left; margin-left:40px;">
	 						<label><input checked name = "type" type="radio" value="1" onclick="document.getElementById('conf') .style.display='';document.getElementById('journ') .style.display='none'">
	 							Conference
	 						</label>
	 					</div>

	 					<div class="radio search-chbox" style="float:left;">
	 						<label><input name = "type" type="radio" value="0" onclick="document.getElementById('conf') .style.display='none';document.getElementById('journ') .style.display=''">
	 							Journal
	 						</label>
	 					</div>
	 					<br>
	 					<br>
	 					<div id="conf"  align="center"> 
	 						<input type="number" class="form-control elem-mgn" name="id_to" placeholder="Enter conference id">
	 					</div> 
	 					<div id="journ" style="display:none" align="center"> 
	 						<input type="number" class="form-control elem-mgn" name="id_to" placeholder="Enter issue of journal id">
	 					</div> 
	 					<br>
	 					<div class="col-lg-6">
		 					<input type="text" name="begin_page" class="form-control" placeholder="Enter begin page"/>
	 					</div>
	 					<div class="col-lg-6">
		 					<input type="text" name="end_page" class="form-control" placeholder="Enter end page"/>			
	 					</div>
	 					<br>
	 					<br>
	 					<button type="button" class=" btn reg-btn search-btn" onclick="addFields()" >Add author</button> 
	 					<div id = "authors"/>
	 				</div>
	 				<br>
	 				<button type="submit" class=" btn reg-btn search-btn" >Add article</button> 
	 			</div>
	 		</form>
	 	</div>
	 </div>
	 <script type='text/javascript'>
	 	function addFields(){
	 		$('#authors').append('<label for="author" class="control-label pull-left">Author</label>')
	 		$('#authors').append('<input type="text" name="author[]" class="my form-control" placeholder="Enter author"/>')
	 	}
	 </script>''')