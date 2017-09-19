from bs4 import BeautifulSoup
import requests

def getDepthHtml(teamOurLandsUrl):

	# Scrape the HTML at the url
	r = requests.get(teamOurLandsUrl)

	# Turn the HTML into a Beautiful Soup object
	soup = BeautifulSoup(r.text, 'html.parser')

	[s.extract() for s in soup('th')]

	table = soup.find(class_='col-md-12 blog-page')

	links = table.find_all('a')

	for link in links:
	    link['target'] = '_blank'

	return table