import sys, re, requests
from parser import *
from database import *
import threading

#imports 500000 journal articles
def import_journal_articles():

	print('started!')
	db = DataBase('postgres', 'postgres', 5433, 'publications')
	parser = Parser(db)
	#get all data from database
	parser.fetch_journ()

	for i in range(1, 500):
		
		print('////////////////////////// imported:' + str((i-1)*1000))
		t = 100
		#if time more then 50 seconds, xml file can be broken, so repeat download
		while t > 50:
			start_time = time.time()
			req = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?ctype=Journals&rs=%(r)s&hc=1000' % {'r': str(int(i-1) + (int(i)-1)*1000)}
			response = requests.get(req).text
			t = (time.time() - start_time)

			print("--- %s getted ---" % t)
		#parse response
		parser.parse_journ_article(response)

def import_conf_articles():

	print('started!')
	db = DataBase('postgres', 'postgres', 5433, 'publications')
	parser = Parser(db)
	#get all data from database
	parser.fetch_conf()
	for i in range(1, 500):
		print('////////////////////////// imported:' + str((i-1)*1000))
		t = 100
		#if time more then 50 seconds, xml file can be broken, so repeat download
		while t > 50:
			start_time = time.time()
			req = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?ctype=Conferences&rs=%(r)s&hc=1000' % {'r': str(int(i-1) + (int(i)-1)*1000)}
			response = requests.get(req).text
			t = (time.time() - start_time)
			print("--- %s getted ---" % t)
		#parse response
		parser.parse_conf_article(response)

if __name__ == '__main__':
	#if you want to import journal articles, uncomment first line, else - uncomment second line
	#import_journal_articles()
	#import_conf_articles()
	pass