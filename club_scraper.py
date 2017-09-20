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

	### search events in the page
	# connect to the event page
	eventBsObj = getConnection("http://www.clubberia.com" + url)
	# find all events in the page
	events = eventBsObj.findAll("dl", {"class":"landscape"})
	for event in events:
		# if fav genre then go to the readmore page
		genres = event.findAll("div", {"class":"genre"})
		for genre in genres:
			if genre.get_text().lower() in fav_genres:
				readmore_url = event.find("dt").find("a").attrs['href']
				readmoreUrls.add(readmore_url)

	### get detail info of each event and print em
	for readmoreUrl in readmoreUrls:
		detailBsObj = getConnection("http://www.clubberia.com"+readmoreUrl)	
		detail = detailBsObj.find("div", {"class":"visualTop"})
		# pick up required info
		date = detail.find("item", {"itemprop":"startDate"}).get_text()
		if re.search("^.*(Fri).*$", date) is None and re.search("^.*(Sat).*$", date) is None:
			continue		
		name = detail.find("h2").get_text()
		genre = ''
		tmp_genres = detail.findAll("div", {"class":"genre"})
		dirty = False
		for tmp_genre in tmp_genres:
			if not dirty:
				genre += tmp_genre.get_text()
				dirty = True
			else:
				genre += (", " + tmp_genre.get_text())
		venue = detail.find("item", {"itemprop":"location"}).find("a").find("item").get_text()
		fee = detail.findChild("span", recursive=False)
		if fee is None:
			fee = ""
		else:
			fee = fee.get_text()
		tmp_discount = detail.find("div", {"class":"ticketservices"})
		if tmp_discount is None:
			discount = "No"
		else:
			discount = "Yes"
		dj = ''
		tmp_djs = detail.findAll("a", href=re.compile("^(/ja/artists/).*$"))
		dirty = False
		for tmp_dj in tmp_djs:
			if not dirty:
				dj += tmp_dj.get_text()
				dirty = True
			else:
				dj += (", " + tmp_dj.get_text())
		# print the event list 
		print("-------------")
		print("Event: %s\nGenre: %s\nVenue: %s\nDate: %s\nFee: %s\nDiscount: %s\nLineup: %s\nURL: http://www.clubberia.com%s\n" %(name,genre,venue,date,fee,discount,dj,readmoreUrl))

	# move on to the next page
	nextPage = eventBsObj.find("p", {"id":"pageNext"})
	nextPageUrl = nextPage.find("a")
	if nextPageUrl is not None:
		nextPageUrl = nextPageUrl.attrs['href']
	else:
		return
	getEventInfo(nextPageUrl)
# def getEventInfo End #

# start here
if __name__ == "__main__":
	getEventInfo("/ja/events/japan/tokyo/")
