from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import requests

fav_genres = ["dubstep", "edm", "hiphop"]

#-------------------------------#
# function: connect to the page 
#-------------------------------#
def getConnection(url):
	try:
		session = requests.Session()
		headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)""AppleWebKit 537.36 (KHTML, like Gecko Chrome", "Accept":"text/html,application/xhtml+xml,application/xml;""q=0.9,image/webp,*/*;q=0.8"}
		req = session.get(url, headers=headers)
	except HTTPError as e:
		print(e)
		return None
	except URLError as e:
		print("Not found")
		return None
	return BeautifulSoup(req.text, "html.parser")
# def getConnection End #

#----------------------------------------------------------#
# function: collect information of each event in each page
#----------------------------------------------------------#
def getEventInfo(url):
	readmoreUrls = set()

	### search event in the page
	# connect to the event page
	eventBsObj = getConnection("https://www.clubberia.com"+url)
	# find all events in page
	events = eventBsObj.findAll("div", {"class":"c-post__frame"})
	for event in events:
		# find fav genre and go to sp page
		genres = event.findAll("div", {"class":"c-post__genre"})
		for genre in genres:
			if genre.get_text().lower() in fav_genres:
				readmore_url = event.find("a").attrs['href']
				readmoreUrls.add(readmore_url)

	### get detail info of each event and print'em
	for readmoreUrl in readmoreUrls:
		detailBsObj = getConnection("http://www.clubberia.com"+readmoreUrl)	
		detail = detailBsObj.find("article", {"class":"c-article"})

		# pick up required information	
		name = detail.find("h1", {"class":"c-article__heading"}).get_text()
		
		genre = ''
		tmp_genres = detail.findAll("div", {"class":"c-post__genre"})
		dirty = False
		for tmp_genre in tmp_genres:
			if not dirty:
				genre += tmp_genre.get_text()
				dirty = True
			else:
				genre += (", " + tmp_genre.get_text())

		data_dl = detail.find("dl", {"class":"c-article-info"})
		data_dt_all = data_dl.findAll("dt", {"class":"c-article-info__term"})
		data_dd_all = data_dl.findAll("dd", {"class":"c-article-info__description"})

		# print the event list 
		print("-------------")
		print("Event: %s\nGenre: %s\n" %(name,genre))
		print("More Info:")
		for data_dt, data_dd in zip(data_dt_all, data_dd_all):
			print(" %s\n %s" %(data_dt.get_text().strip(), data_dd.get_text().strip()))
		print("URL: http://www.clubberia.com%s\n" %(readmoreUrl))

	# move on to the next page
	nextPage = eventBsObj.find("div", {"class":"p-events-filter__arrow--next"})
	nextPageUrl = nextPage.find("a")
	if nextPageUrl is not None:
		nextPageUrl = nextPageUrl.attrs['href']
	else:
		return
	getEventInfo(nextPageUrl)
# def getEventInfo End #

# start here
if __name__ == "__main__":
	getEventInfo("/ja/events/?action_Event_List=true&region_cd=tokyo&genre_cd=&option=&keyword=&schedule_date=&submit=SEARCH")
