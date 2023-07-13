from flask import Flask
from flask import render_template , request,redirect,url_for
import sqlite3 as sql
import random
app = Flask(__name__)

#GLOBAL VARIABLES
ROW_ID=0
USER="User"
MSG="Welcome Admin"
MOVIE=""
VENUE=""
SHOW_NO=""
NO_OF_TICKETS=0
DATE=""
EMAIL_ID=""
TID=0
AMOUNT=0

@app.route("/")
def main():
    return render_template('index.html')


@app.route("/showAboutUs")
def showAboutUs():
    return render_template('aboutUs.html')


@app.route("/showNewUserPage/")
def showNewUserPage():
    return render_template('newUser.html')

@app.route("/showloginpage/showNewUserPage/")
def cshowNewUserPage1():
    return render_template("newUser.html")
 
@app.route('/signUp',methods = ['POST', 'GET'])
def signup():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['name']
         phno = request.form['phno']
         email = request.form['email']
         password = request.form['password']
         if not name or not phno  or not email  or not password :
            return render_template('newUser.html')
         else:
            with sql.connect("movie_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO VISITOR (v_name,v_phno,v_email_id,v_password) VALUES (?,?,?,?)",(name,phno,email,password) )
               flag=True
               con.commit()
           
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/showloginpage/")
         else:
            return redirect("/showNewUserPage/")
       
      
      

@app.route('/showloginpage/')
def cshowloginpage():
   return render_template("login.html")

@app.route('/login',methods = ['POST', 'GET'])
def login():
   flag=False
   
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("select v_email_id,v_password,v_name from visitor")
            rows=cur.fetchall()
            cur.execute("select name,password from admin")
            adetails=cur.fetchall()
            for adetail in adetails:
               dbemail=adetail[0]
               dbPass=adetail[1]
               if dbemail == email and dbPass == password:
                  global USER , EMAIL_ID 
                  USER="ADMIN"
                  return redirect("/adminDashboard/")
               else:
                  flag=False
            for row in rows:
               dbemail=row[0]
               dbPass=row[1]
               if dbemail == email and dbPass == password:
                  flag=True 
                  EMAIL_ID=dbemail
                  USER=row[2]

                  break
               else:
                  flag=False
   con.commit()
   if(flag==True):
      return redirect("/showmovies/")
   else:
      return redirect("/")
@app.route('/adminDashboard/showmovies/')
@app.route('/showmovies/')
def showmovies():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select m_name,m_rating,m_language,m_synopsis from movie order by m_release desc")
      rows=cur.fetchall()
      return render_template("movies.html",USER=USER,rows=rows)


@app.route('/showmovies/showBookTickets/')
def showBookTickets():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select m_name from movie")
      mnames=cur.fetchall()
      cur.execute("select v_name from venue")
      vnames=cur.fetchall()
      return render_template("tickets.html",USER=USER,mnames=mnames,vnames=vnames)


@app.route('/checkAvail',methods = ['POST', 'GET'])
def availability():
   flag=False
   print('INSIDE')
   if request.method == 'POST':
      movie = request.form['movie']
      venue = request.form['venue']
      show_no = request.form['show_no']
      no_of_tickets = request.form['no_of_tickets']
      date = request.form['date']
      movie=movie[2:-3].strip()
      venue=venue[2:-3].strip()
      global MOVIE,VENUE,SHOW_NO,NO_OF_TICKETS,DATE
      MOVIE=movie
      VENUE=venue
      SHOW_NO=show_no
      NO_OF_TICKETS=no_of_tickets
      DATE=date
      with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("select v_capacity from venue where v_name=?",(venue,))
            v_capacity=str(cur.fetchall())
            no=int(v_capacity[2:-3])
            print(no)
            try:
               cur.execute("select no_of_tickets from book_ticket where m_name = ? and v_name = ? and show_no = ? and date = ?",(movie,venue,show_no,date))
               seatsAvailable=cur.fetchone()
            finally:
               seatsAvailable=0
            
   
            print(seatsAvailable)
            if(no>seatsAvailable):
               return redirect("/payment")
            else:
               return render_template("tickets.html")
   con.commit()
   if(flag==True):
      return redirect("/showmovies/")
   else:
      return redirect("/")


@app.route('/payment/')
def pay():
   global NO_OF_TICKETS,USER,MOVIE,VENUE,SHOW_NO,NO_OF_TICKETS,DATE,EMAIL_ID,AMOUNT,TID
   cost=int(NO_OF_TICKETS)*100
   AMOUNT=cost
   tid=random.randint(1,1000)
   TID=tid
   return render_template('payment.html',cost=cost,user=USER,movie=MOVIE,venue=VENUE,show_no=SHOW_NO,tickets=NO_OF_TICKETS,date=DATE,email=EMAIL_ID,tid=tid)

@app.route('/book',methods = ['POST', 'GET'])
def book():
   flag=False
   print('INSIDE')
   if request.method == 'POST':
      global MOVIE,VENUE,SHOW_NO,NO_OF_TICKETS,DATE,EMAIL_ID,TID,AMOUNT
      print(MOVIE)
      print(VENUE)
      print(SHOW_NO)
      print(NO_OF_TICKETS)
      print(DATE)
      print(EMAIL_ID)
      print(TID)
      print(AMOUNT)
      with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO BOOK_TICKET(NO_OF_TICKETS,M_NAME,SHOW_NO,DATE,V_NAME,V_EMAIL_ID) VALUES (?,?,?,?,?,?)",(NO_OF_TICKETS,MOVIE,SHOW_NO,DATE,VENUE,EMAIL_ID))
            print("insert into book_ticket success")
            cur.execute("INSERT INTO PAYMENT(V_EMAIL_ID,AMOUNT,TRANSACTION_ID) VALUES (?,?,?)",(EMAIL_ID,AMOUNT,TID))
            print("insert into PAYMENT success")
            flag=True
            
      con.commit()
   if(flag==True):
      return redirect(url_for('showmovies'))
   else:
      return redirect(url_for('showmovies'))


@app.route('/adminDashboard/addMovie/')
def showaddMovie():
   return render_template("addmovie.html")


@app.route('/addmovie',methods = ['POST', 'GET'])
def addmovie():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['name']
         rating = request.form['rating']
         release = request.form['release']
         language = request.form['language']
         synopsis = request.form['synopsis']
         print(name)
         if not name or not rating  or not release  or not language or not synopsis :
            return render_template('addmovie.html')
         else:
            with sql.connect("movie_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO movie (m_name,m_rating,m_release,m_language,m_synopsis) VALUES (?,?,?,?,?)",(name,rating,release,language,synopsis) )
               flag=True
               con.commit()
              
           
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/adminDashboard/")


@app.route('/removeMovie/')
@app.route('/adminDashboard/removeMovie/')
def showremoveMovie():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select m_name from movie")
      mnames=cur.fetchall()
      return render_template("removeMovie.html",mnames=mnames)

@app.route('/removeMovie',methods = ['POST', 'GET'])
def removemovie():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['movie']
         
         name=name[2:-3].strip()
         name=name
         with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            print("BEFORE QUERY")
            cur.execute("DELETE FROM movie WHERE m_name= ?",(name,))
            print("afTER  QUERY")
            flag=True
            con.commit()
            con.close()           
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/removeMovie/")


@app.route('/removevenue/')
@app.route('/adminDashboard/removevenue/')
def showremovevenue():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select v_name from venue")
      vnames=cur.fetchall()
      return render_template("removevenue.html",vnames=vnames)

@app.route('/removevenue',methods = ['POST', 'GET'])
def removevenue():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['venue']
         
         name=name[2:-3].strip()
         name=name
         with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            print("BEFORE QUERY")
            cur.execute("DELETE FROM venue WHERE v_name= ?",(name,))
            print("afTER  QUERY")
            flag=True
            con.commit()
            con.close()     
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/removevenue/")
         

@app.route('/adminDashboard/addvenue/')
def showaddvenue():
   return render_template("addvenue.html")


@app.route('/addvenue',methods = ['POST', 'GET'])
def addvenue():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['name']
         capacity = request.form['capacity']
         id = request.form['id']
         
         print(name)
         if not name or not capacity   :
            return render_template('addvenue.html')
         else:
            with sql.connect("movie_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO venue (v_name,v_capacity,v_id) VALUES (?,?,?)",(name,capacity,id) )
               flag=True
               con.commit()
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/adminDashboard/")
         
         
@app.route("/adminlogin1/")
def adminlogin1():
    return render_template("adminlogin.html")


@app.route('/adminlogin',methods = ['POST', 'GET'])
def adminlogin():
   error = None
   if request.method == 'POST':
        if request.form['username'] == "admin" or request.form['password'] == "admin":
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/adminlogin')
   #return render_template("admin.html", error=error)
   return redirect("/adminDashboard")

@app.route("/adminDashboard/")
def adminDashboard():
    return render_template("admin.html")
 
if __name__ == "__main__":
    app.run(debug=True)