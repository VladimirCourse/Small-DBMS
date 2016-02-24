import postgresql

#class which works with database
class DataBase:

	def __init__(self, user, passw, port, dbname):
		self.db = postgresql.open(user = user, 
								  password = passw, 
								  port = port, 
								  database = dbname)
	#get request as dict, key is id
	def req_dict(self, req):
		res = self.db.prepare(req)
		dres = {}
		for i in res:
			dres[tuple(i[j] for j in range(1, len(i)))] = i[0]
		return dres
	#get request as set
	def req_set(self, req):
		res = self.db.prepare(req)
		sres = set()
		for i in res:
			sres.add(tuple(i))
		return sres
	#simple request
	def req(self, req_t):
		return self.db.prepare(req_t)()
	#insert request
	def insert_rows(self, query, rows):
		mk = self.db.prepare(query)
		mk.load_rows(rows)
	#query
	def query(self, req, cond):
		res = self.db.prepare(req)
		return res(*cond)

