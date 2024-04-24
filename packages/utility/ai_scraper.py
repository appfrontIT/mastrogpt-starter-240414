def main(args):
    # Importing necessary libraries
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    from collections import deque
    
    if args.get('url'):
        # Step 1: Take the input URL provided when the action is invoked
        input_url = args['url']
        
        # Step 2: Use the input URL to access the webpage content
        response = requests.get(input_url)
        
        # Step 3: Extract all the textual data from the webpage
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = ' '.join([p.text for p in soup.find_all('p')])
        
        # Step 4: Generate a summary of the textual content extracted from the webpage
        # Dummy summary generation
        summary = 'This is a dummy summary for the webpage'
        
        # Step 5: Recursively scan each link within the webpage
        domain = input_url.split('/')[2]
        visited = set()
        links_to_visit = deque([input_url])
        while links_to_visit:
            current_url = links_to_visit.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)
            
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                if link.get('href') and domain in link.get('href'):
                    new_url = urljoin(current_url, link.get('href'))
                    if new_url not in visited:
                        links_to_visit.append(new_url)
        
        # Step 6: Create an array to store the information of each scanned page
        pages_map = {}
        for page_url in visited:
            page_data = {
                'URL': page_url,
                'Summary': summary,
                'Textual Content': text_data
            }
            pages_map += page_data
        
        # Step 7: Save the scanned data inside the database
        import json
        import requests
        db_data = {
            "add": True,
            "collection": "scanned_pages",
            "data": pages_map
        }
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json=db_data)
        return {"body": response.text}
    else:
        return {"body": "Error: URL parameter is missing."}