import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_current_date():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

def get_weather():
    location = "Arlington,VA,US"
    weather_url = f"https://wttr.in/{location}?format=%C+%t"
    response = requests.get(weather_url)
    return f"The current weather in Arlington, VA is {response.text}."

def get_top_news_stories():
    news_url = "https://techcrunch.com/"
    response = requests.get(news_url)
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.select(".post-block__title__link")
    top_stories = [{"title": headline.text.strip(), "link": headline["href"]} for headline in headlines[:5]]
    return top_stories

def get_stock_market_news():
    news_url = "https://www.marketwatch.com/latest-news?mod=top_nav"
    response = requests.get(news_url)
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.select(".article__headline .link")
    top_stories = [{"title": headline.text.strip(), "link": headline["href"]} for headline in headlines[:5]]
    return top_stories

def get_history_event_of_the_day():
    url = "https://www.onthisday.com/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        event_element = soup.find("li", class_="event")
        
        if event_element:
            event_text = event_element.get_text().strip()
            return event_text
        else:
            return "Error finding the historical event element"
    else:
        return "Error fetching historical event"

summary = []

current_date = get_current_date()
summary.append(f"Today's date: {current_date}")

event_of_the_day = get_history_event_of_the_day()
summary.append(f"Today in history: {event_of_the_day}")

weather = get_weather()
summary.append(weather)

summary.append("\nTop tech news stories:")
top_stories = get_top_news_stories()
for story in top_stories:
    summary.append(f"{story['title']} - {story['link']}")

summary.append("\nStock market news:")
stock_stories = get_stock_market_news()
for story in stock_stories:
    summary.append(f"{story['title']} - {story['link']}")

# Print all elements of the summary list
for element in summary:
    print(element)
