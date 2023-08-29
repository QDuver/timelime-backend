

from googleapiclient.discovery import build
API_KEY = "AIzaSyBl9-P8iSKJ_VXNAFnaaFPqb1XNaWVeluI"
SEARCH_ENGINE_ID = "90d862b25c6fc454e"

def google_search(query):
    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType="image").execute()
    return result.get("items", [])

query = "Python programming"
results = google_search(query)

for i, result in enumerate(results, start=1):
    print(f"Result {i}:")
    print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    print(f"Snippet: {result.get('snippet', 'N/A')}")
    print("="*40)