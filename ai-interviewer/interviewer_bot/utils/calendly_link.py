
import requests
import os
from datetime import datetime, timezone


# when creating a scheduling event in calendly, can set the "location" to zoom.
# helpful info; 
# https://help.calendly.com/hc/en-us/articles/14075911977623-Calendly-Zoom#1

# calendly api key can be accessed here
# https://calendly.com/integrations/api_webhooks

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")


def extract_zoom_link(location):
    """Handles both dict and string-based location fields"""
    if isinstance(location, str):
        if "zoom.us" in location:
            return location.split(" - ")[-1].strip()
    elif isinstance(location, dict):
        return location.get("join_url")
    return None


def get_all_zoom_links() -> list:
    """
    Gathers all the zoom links for a given user

    Parameters: 
        None
        
    Returns: 
        zoom_links : list
            list of zoom links with the given zoom link, start time, and candidate name
    """
    headers = { "Authorization": f"Bearer {CALENDLY_API_KEY}"}

    # Calendly user URI
    user_resp = requests.get("https://api.calendly.com/users/me", headers=headers)
    if user_resp.status_code != 200:
        print("Failed to get user info:", user_resp.text)
        return []

    user_uri = user_resp.json()["resource"]["uri"]

    # get all scheduled events for that user
    params = {"user": user_uri, "sort": "start_time:desc"}
    zoom_links = []

    while True:
        events_resp = requests.get("https://api.calendly.com/scheduled_events", headers=headers, params=params)
        if events_resp.status_code != 200:
            print("Failed to get events:", events_resp.text)
            break

        events = events_resp.json().get("collection", [])
        for event in events:
            zoom_link = extract_zoom_link(event.get("location"))
            if zoom_link:
                zoom_links.append({
                    "zoom_link": zoom_link,
                    "start_time": event.get("start_time"),
                    "name": event.get("name")
                })

        # Handle pagination
        next_page = events_resp.json().get("pagination", {}).get("next_page")
        if next_page:
            params = {}  # Empty because next_page URL already includes query params
            url = next_page
        else:
            break

    return zoom_links



# def get_earliest_zoom_link():
#     """Returns the earliest scheduled Zoom meeting link only"""
#     links = get_all_zoom_links()
#     if not links:
#         return None

#     # Sort by start_time ascending (earliest first)
#     links.sort(key=lambda x: x["start_time"])
#     return links[0]["zoom_link"]

def get_earliest_calendly_zoom_link():
    """Returns the earliest upcoming zoom meeting link only."""
    links = get_all_zoom_links()
    if not links:
        return None

    # ignore past events
    now = datetime.now(timezone.utc)
    future_links = [link for link in links if datetime.fromisoformat(link["start_time"].replace("Z", "+00:00")) > now]

    if not future_links:
        print("No future Zoom meetings found.")
        return None

    # sort future links by start_time ascending to get earliest one
    future_links.sort(key=lambda x: x["start_time"])
    return future_links[0]["zoom_link"]

if __name__ == "__main__":

    # # get all links
    # links = get_all_zoom_links()
    # if links:
    #     for entry in links:
    #         print("\n" , entry)
    #         #print(f"\n{entry['start_time']}   —   {entry['zoom_link']}\n")
    # else:
    #     print("No Zoom links found.")
    
    # only get the earliest zoom link
    link = get_earliest_calendly_zoom_link()
    if link:
        print("\nearliest zoom Link[CALEDNLY]: ", link)
    else:
        print("\nzo zoom links found.[CALENDLY]")

    


