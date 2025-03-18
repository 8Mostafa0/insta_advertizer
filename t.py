import json

def get_explore_data(session):
    try:
        url = "https://www.instagram.com/api/graphql/"
        payload = {
            "query_hash": "YOUR_QUERY_HASH_HERE",  # Replace with actual hash
            "variables": json.dumps({"first": 12, "after": ""})
        }
        response = session.post(url, data=payload, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        print(f"Explore request: Status {response.status_code}")
        print(f"Explore response: {response.text[:200]}...")
        if response.status_code == 200:
            data = response.json()
            # Adjust based on actual response structure
            posts = data.get("data", {}).get("explore", {}).get("edges", [])
            posts = [edge["node"] for edge in posts if "node" in edge]
            print(f"Fetched {len(posts)} explore posts")
            return posts
        print(f"Failed to fetch explore data: HTTP {response.status_code}")
        return []
    except Exception as e:
        print(f"Error fetching explore data: {str(e)}")
        return []

get_explore_data()