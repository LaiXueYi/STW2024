from flask import Flask, render_template, request
import sqlite3
import datetime

from flask.templating import render_template_string

app = Flask(__name__)

conn = sqlite3.connect('recos.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS recos(rid INTEGER PRIMARY KEY, reco TEXT)')
conn.commit()
conn.close()

conn = sqlite3.connect("keeptrack.db")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS keeptrack(
date TEXT,
subject TEXT, 
stime INTEGER, 
game TEXT, 
ptime INTEGER)''')
conn.commit()
conn.close()

def insert_reco(data):
    conn = sqlite3.connect('recos.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO recos(reco) VALUES(?)', (data,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/improve', methods=['GET', 'POST'])
def improve():
  if request.method == 'POST':
    ans = request.form['answer']
    # print(ans)
    if ans == 'yes':
      return render_template('welldone.html')
    else: 
      return render_template('create.html')
  return render_template('improve.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
  recos = []
  if request.method == 'POST':
    ccaday = request.form.get('ccaeven', '')
    ans = request.form.get('answer', '')
    relieve = request.form.get('sport', '')
    #print(ccaday)
    if ccaday == 'ccaeven':
      recos.append('You should try to get work done on odd days')
    else:
      recos.append('You should try to get work done on even days')
    if ans == 'yes':
      recos.append('You should spend more time resting and relaxing after cca')
    else:
      recos.append('You should spend more time studying after cca')
    if relieve == 'sport':
      recos.append('You should study more at night and play sports with your friends after school')
    else:
      recos.append('You should study more after school and use your phone at night to relieve your stress')
    # print(recos)
    # print(recos[1])
    insert_reco(recos[0])
    insert_reco(recos[1])
    insert_reco(recos[2])
    return render_template('reco.html', recos=recos)
  return render_template('create.html')
  
@app.route('/reco')
def reco():
  conn = sqlite3.connect('recos.db')
  cur = conn.cursor()
  cur.execute('SELECT reco FROM recos ORDER BY rid DESC LIMIT 3;')
  records = cur.fetchall()
  recos = []
  for record in records:
    temp = str(record[0])
    recos.append(temp)
  conn.close()
  return render_template('reco.html', recos=recos)

@app.route('/keeptrack', methods=['GET', 'POST'])
def keeptrack():
  curr_date = str(datetime.date.today())
  conn = sqlite3.connect("keeptrack.db")
  cur = conn.cursor()
  if request.method == 'POST':
    subject = request.form["subject"]
    stime = int(request.form["study"])
    game = request.form["game"]
    ptime = int(request.form["play"])
    cur.execute('INSERT INTO keeptrack(date, subject, stime, game, ptime) VALUES(?,?,?,?,?)', (curr_date, subject, stime, game, ptime))
    conn.commit()
    cur.execute('''SELECT subject, stime, game, ptime FROM keeptrack
                   WHERE date = ?''', (curr_date,))
    records = cur.fetchall()
    conn.close()
    return render_template('keeptrack.html', records=records)
    
  cur.execute('SELECT subject, stime, game, ptime FROM keeptrack WHERE date = ?', (curr_date,))
  records = cur.fetchall()

  reminder = []
  cur.execute('SELECT SUM(stime) FROM keeptrack WHERE date = ?', (curr_date,))
  tstime = cur.fetchone()[0]
  cur.execute('SELECT SUM(ptime) FROM keeptrack WHERE date = ?', (curr_date,))
  tptime = cur.fetchone()[0]
  if tstime >= 4 and tptime >=3:
    reminder.append(' You have studied and play for motre than 7 hours. How do you have so much time? Are you sleeping ?!?')
  elif tstime >= 4:
    reminder.append(f'You have studied for {tstime} hours today, you can take a break')
  elif tptime >= 3:
    reminder.append(f'You have played for {tptime} hours today, you should start studying')
  return render_template('keeptrack.html', records=records, reminder=reminder)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
