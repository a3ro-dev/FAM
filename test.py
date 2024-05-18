    

def getNews():
        import requests
        api_key = "67971eebe05d4dffaed478cf1560f4cd"
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        articles = data["articles"]
        return articles

print(getNews())