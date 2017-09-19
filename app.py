import flask
from flask import *
from helpers import *
from bs4 import BeautifulSoup
from twit import *
from pymongo import MongoClient

client = MongoClient()
spDb = client.sp

teamsCol = spDb['teams']
gamesCol = spDb['games']

app = flask.Flask(__name__)
app.secret_key = 'aaabbbbccc'


@app.route('/<week>/<gameId>',methods=['GET','POST'])
def game(week,gameId):
	if request.method == 'GET':
		#get each teams data
		awayAbbr, homeAbbr = gameId.split('@')[0], gameId.split('@')[1]

		awayTeam = teamsCol.find_one({"abbr": awayAbbr})
		homeTeam = teamsCol.find_one({"abbr": homeAbbr})

		awayTeam['depthChart'] = Markup(getDepthHtml(awayTeam['depthUrl']))
		homeTeam['depthChart'] = Markup(getDepthHtml(homeTeam['depthUrl']))

		#get teams tweets
		awayTeam['tweets'] = getTeamTweets(awayTeam['beat'])
		homeTeam['tweets'] = getTeamTweets(homeTeam['beat'])

		gameDoc = gamesCol.find_one({"abbrId": gameId})
		return render_template('game.html', homeTeam=homeTeam,awayTeam=awayTeam, gameDoc=gameDoc)
	if request.method == 'POST':
		data = request.form
		k = data.keys()[0]
		v = data.get(k)

		#add new value for game object
		#get games data
		gamesCol.update_one({"abbrId": gameId}, {"$set": {k:v}})
		gameDoc = gamesCol.find_one({"abbrId": gameId})

		#if data is a team score guess
		if k == 'guessScoreHome' or 'guessScoreAway':
			#check scores and determine who is the favorite
			if int(gameDoc['guessScoreAway']) > int(gameDoc['guessScoreHome']):
				gamesCol.update_one({"abbrId": gameId}, {"$set": {"fav":gameDoc["away"]}})
				gamesCol.update_one({"abbrId": gameId}, {"$set": {"dog":gameDoc["home"]}})
			else:
				gamesCol.update_one({"abbrId": gameId}, {"$set": {"dog":gameDoc["away"]}})
				gamesCol.update_one({"abbrId": gameId}, {"$set": {"fav":gameDoc["home"]}})
		return 'updated'

@app.route('/notes/<abbr>',methods=['GET','POST'])
def notes(abbr):
	if request.method == 'POST':
		abbr = request.form.get('team')
		note = request.form.get('note')

		if '@' in abbr:
			gamesCol.update_one({"abbrId": abbr}, {"$push": {"notes" :{"$each":[note],"$position":0}}})
			return 'added'
		else:
			#insert note into teams notes
			#teamDoc = teamsCol.find_one({"abbr": abbr})
			teamsCol.update_one({"abbr": abbr}, {"$push": {"notes" :{"$each":[note],"$position":0}}})
			return 'added'

@app.route('/values/<week>')
def values():
	#get games data
	#with open('games.json') as data_file:
	#    games = json.load(data_file)

	#weekGames = games[week]

	#get pulled odds, returns list of game dicts
	#pulledGames = getGamesOdds()
	#for weekGame in weekGames:
		#pass
	#try getting first lines posting of weeks
	return render_template('values.html')
#post /<gameId>/

if __name__ == '__main__':
    app.run(debug = True, port=5002)