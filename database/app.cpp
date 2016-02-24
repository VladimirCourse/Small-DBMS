#include <iostream>
#include <fstream>
#include <iterator>
#include "ServerSocket.h"
#include "SocketException.h"
#include "database.h"

//creating database, if need it
  /*
    db.request("CREATE TABLE article id,int,8,title,str,256,doi,str,32,text_url,str,64,type,int,1 INDEX article_pkey id");
   db.request("CREATE TABLE author id,int,8,name,str,64,institute,str,32 INDEX author_pkey id");
    db.request("CREATE TABLE keyword id,int,8,title,str,64 INDEX keyword_pkey id");
   db.request("CREATE TABLE publisher id,int,8,name,str,64 INDEX publisher_pkey id");
    db.request("CREATE TABLE conference id,int,8,title,str,64,issn,str,32,isbn,str,32,publisher_id,int,8 INDEX conference_pkey id");
    db.request("CREATE TABLE journal id,int,8,title,str,64,issn,str,32,publisher_id,int,8 INDEX journal_pkey id");
    db.request("CREATE TABLE issue id,int,8,journal_id,int,8,issue_ser,str,32,volume,str,32,year,int,4 INDEX issue_pkey id");
    db.request("CREATE TABLE user id,int,8,first_name,str,64,last_name,str,64,email,str,32,password,str,64,priveleges,int,1 INDEX user_pkey id");
    db.request("CREATE TABLE article_rank user_id,int,8,article_id,int,8,rate,int,8,visit_count,int,8 INDEX rank_pkey user_id,article_id");
    db.request("CREATE TABLE articles_authors article_id,int,8,author_id,int,8 INDEX art_auth_pkey article_id,author_id");
    db.request("CREATE TABLE articles_conferences article_id,int,8,conf_id,int,8,begin_page,str,32,end_page,str,32 INDEX art_conf_pkey article_id,conf_id");
  db.request("CREATE TABLE articles_issues article_id,int,8,issue_id,int,8,begin_page,str,32,end_page,str,32 INDEX art_issue_pkey article_id,issue_id");
  db.request("CREATE TABLE articles_keywords article_id,int,8,keyword_id,int,8 INDEX art_keyw_pkey article_id,keyword_id");*/

int main(){
	
 	Database db("database");
  //listening requests
  try{
      // Create the socket
    ServerSocket server ( 30000 );
    while(true){
      ServerSocket new_sock;
      server.accept (new_sock);
      try{
        std::string data;
        new_sock >> data;
        std::string *res = db.request(data);
        new_sock << *res;
        delete res;
      }catch (SocketException& e){
        std::cout << "Something go wrong: " << e.description() << "\nExiting.\n";
      }

    }
  }
  catch (SocketException& e){
    std::cout << "Something go wrong: " << e.description() << "\nExiting.\n";
  }

  return 0;
}
