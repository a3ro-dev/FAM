import requests
import json

def search(topic: str):
    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": "YOUR_SUBSCRIPTION_KEY"}
        params = {'q': topic}

        response = requests.get(url, headers=headers, params=params)
        results = json.loads(response.text)

        # Check if any results were found
        if 'webPages' in results and 'value' in results['webPages']:
            # Get the first result
            first_result = results['webPages']['value'][0]

            # Find the name and url
            name = first_result['name']
            url = first_result['url']

            return name, url
        else:
            return "No results found"
    except Exception as e:
        print(f"Error in search: {e}")

# Example usage:
first_result = search('Python programming')
print(first_result)