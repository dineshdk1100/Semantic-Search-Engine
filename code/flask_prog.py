from multiprocessing import Process
from flask import Flask, redirect, url_for, request,render_template
from searching import queryProcessing


app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')


@app.route('/files/<filename>')
def files(filename):
   qp=queryProcessing()
   res=qp.file_return(filename)
   return render_template("files.html",result=res)


@app.route('/search/<words>',methods=["POST","GET"])
def queries(words):
   qp = queryProcessing()
   if words=="start":
      query=request.form['query']
   else:
      query=words
   p=qp.starting_search(query)
   suggestion=p['suggestion']
   wiki=p['wikipedia']
   del p['wikipedia']
   del p['suggestion']
   if len(p) >0:
      return render_template("result.html", result=p,result2=query,result3=wiki,suggestions=suggestion)
   else:
      return render_template("noresult.html")

if __name__ == '__main__':
   app.run()