import requests

def test_api_endpoint():
    base_url = "https://7s5jpj4mtg.execute-api.us-east-1.amazonaws.com/dev"
    entity = "payment"
    
    # Construct the full URL
    url = f"{base_url}/{entity}"
    
    try:
        # Make the GET request to the endpoint
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Success!")
            print("Response JSON:")
            print(response.json())
        else:
            print(f"Failed with status code: {response.status_code}")
            print("Response text:")
            print(response.text)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_api_endpoint()
