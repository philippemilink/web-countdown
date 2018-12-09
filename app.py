from flask import Flask
from flask import render_template
from flask import jsonify
from flask import redirect
from flask import url_for
import time
import datetime
import sqlite3 as sql

DATABASE = "database.db"


app = Flask(__name__)


def get_current_talk():
	con = sql.connect(DATABASE)
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM talks WHERE real_start_hour IS NOT NULL AND real_length_minutes IS NULL ORDER BY real_start_hour DESC, real_start_minute DESC LIMIT 0, 1")

	talk = cur.fetchone();
	con.close()

	return talk


@app.route('/')
def home():
	con = sql.connect(DATABASE)
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM talks ORDER BY real_start_hour, real_start_minute, start_hour, start_minute")

	rows = cur.fetchall();
	con.close()


	return render_template("index.html", talks=rows, current_talk=get_current_talk())


@app.route('/start_talk/<int:talk_id>')
def start_talk(talk_id):
	con = sql.connect(DATABASE)
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("UPDATE talks SET real_start_hour=?, real_start_minute=? WHERE id = ?", 
		(time.localtime().tm_hour, time.localtime().tm_min, talk_id))

	con.commit()

	con.close()

	return redirect(url_for('home'))


@app.route('/stop_talk/<int:talk_id>')
def stop_talk(talk_id):
	con = sql.connect(DATABASE)
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM talks WHERE id = ?", (talk_id,))

	talk = cur.fetchone()

	real_start = datetime.datetime.combine(datetime.date.today(), datetime.time(talk["real_start_hour"], talk["real_start_minute"]))
	
	time_length = datetime.datetime.now() - real_start;
	print(time_length.total_seconds() // 60)
	
	cur = con.cursor()
	cur.execute("UPDATE talks SET real_length_minutes=? WHERE id = ?", 
		(time_length.total_seconds() // 60, talk_id))

	con.commit()
	
	con.close()

	return redirect(url_for('home'))


@app.route('/screen')
def screen():
    return render_template('screen.html')

@app.route('/get_scren_data')
def get_scren_data():
	talk = get_current_talk()	

	data = dict()
	data["time"] = time.strftime("%H:%M:%S", time.localtime())

	if talk != None:
		real_start = datetime.datetime.combine(datetime.date.today(), datetime.time(talk["real_start_hour"], talk["real_start_minute"]))
		real_end = real_start + datetime.timedelta(minutes=talk["length_minutes"])

		data["running_talk"] = True
		data["title"] = talk["title"]

		if (datetime.datetime.now() <= real_end):
			hours, remainder = divmod((real_end - datetime.datetime.now()).seconds, 3600)
			minutes, seconds = divmod(remainder, 60) 

			data["chrono"] = '%s <small>min</small>  %s <small>s</small>' % (minutes, seconds)
			data["ended"] = False
			data["less_minute"] = (minutes == 0)
		else:
			hours, remainder = divmod((datetime.datetime.now() - real_end).seconds, 3600)
			minutes, seconds = divmod(remainder, 60) 

			data["chrono"] = '- %s <small>min</small>  %s <small>s</small>' % (minutes, seconds)
			data["ended"] = True
			data["less_minute"] = True
	else:
		data["running_talk"] = False

	return jsonify(**data)
