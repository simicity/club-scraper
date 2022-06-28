import sys
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import requests

fav_genres = ["house", "edm", "hiphop"]
EVENT_SITE_BASE_URL = "https://clubberia.com"

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


def getEventInfo(url, pref_genres):
	readmore_urls = set()
	# connect to the event page
	eventBsObj = getConnection(EVENT_SITE_BASE_URL+url)
	# find all events in page
	events = eventBsObj.find_all("div", {"class":"c-post__frame"})
	for event in events:
		# find fav genre and go to sp page
		event_genres = event.find_all("div", {"class":"c-post__genre"})
		for event_genre in event_genres:
			if event_genre.get_text().lower() in pref_genres:
				readmore_urls.add(event.find("a").attrs['href'])

	for readmore_url in readmore_urls:
		detailBsObj = getConnection(EVENT_SITE_BASE_URL + readmore_url)	
		detail = detailBsObj.find("article", {"class":"c-article"})

		# pick up required information	
		name = detail.find("h1", {"class":"c-article__heading"}).get_text()
		
		genre = ''
		tmp_genres = detail.find_all("div", {"class":"c-post__genre"})
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
		print(f"Event: {name}\nGenre: {genre}")
		print("More Info:")
		for data_dt, data_dd in zip(data_dt_all, data_dd_all):
			print(" %s\n %s" %(data_dt.get_text().strip(), data_dd.get_text().strip()))
		print(f"URL: {EVENT_SITE_BASE_URL}{readmore_url}\n")

	# move on to the next page
	nextPage = eventBsObj.find("div", {"class":"p-events-filter__arrow--next"})
	nextPageUrl = nextPage.find("a")
	if nextPageUrl:
		nextPageUrl = nextPageUrl.attrs['href']
	else:
		return
	getEventInfo(nextPageUrl, pref_genres)


def main():
	if len(sys.argv) >= 2:
		fav_genres = [str(sys.argv[i]) for i in range(1, len(sys.argv))]
		getEventInfo("/ja/events/?action_Event_List=true&region_cd=tokyo&genre_cd=&option=&keyword=&schedule_date=&submit=SEARCH", fav_genres)
	else:
		print("Usage: python club_scraper.py [genre]+")

if __name__ == "__main__":
	main()
