import os
import requests
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FootballAPIClient:
    """
    Client for interacting with the API-Football v3.co API.

    Handles authentication using x-rapidapi-key and x-rapidapi-host headers.
    Provides methods to fetch league standings (teams) and top scorers (players).
    """
    def __init__(self):
        """
        Initializes the API client with credentials from environment variables.
        """
        self.api_key = os.getenv("API_KEY")
        self.api_host = "v3.football.api-sports.io" # As specified in API-Football v3 documentation

        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables. Please set it in your .env file.")

        self.headers = {
            "x-rapidapi-key": self.api_key, # API key required for authentication, obtained from API-Football dashboard
            "x-rapidapi-host": self.api_host # Host header as specified in API-Football v3 documentation
        }
        self.base_url = f"https://{self.api_host}"

    def _make_request(self, endpoint, params=None):
        """
        Makes a GET request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint (e.g., "/standings").
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: JSON response from the API, or None if an error occurred.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request to {url} failed: {e}")
            return None

    def get_standings(self, league_id, season_year):
        """
        Fetches league standings for a specific league and season.

        Args:
            league_id (int): The ID of the league (e.g., 39 for English Premier League).
            season_year (int): The year of the season (e.g., 2023).

        Returns:
            dict: JSON data for league standings, or None.
        """
        endpoint = "/standings"
        params = {"league": league_id, "season": season_year}
        return self._make_request(endpoint, params)

    def get_top_scorers(self, league_id, season_year):
        """
        Fetches top scorers for a specific league and season.

        Args:
            league_id (int): The ID of the league.
            season_year (int): The year of the season.

        Returns:
            dict: JSON data for top scorers, or None.
        """
        endpoint = "/players/topscorers"
        params = {"league": league_id, "season": season_year}
        return self._make_request(endpoint, params)

# Example usage (for testing, will be removed later or moved to a command)
if __name__ == '__main__':
    # This part would typically be in a Django management command or view
    # For standalone testing, ensure API_KEY is set in your shell or .env
    client = FootballAPIClient()
    
    # You would need actual league_id and season_year
    # For EPL (Premier League), league_id is often 39 (as per documentation examples)
    # season_year would be current or past year, e.g., 2023
    league_id = 39 # Example for English Premier League
    season_year = 2023 # Example season

    # Test standings
    print("Fetching standings...")
    standings_data = client.get_standings(league_id, season_year)
    if standings_data and standings_data.get('response'):
        print(f"Standings fetched for League {league_id}, Season {season_year}.")
        # Further processing of standings_data['response'] could go here
    else:
        print("Failed to fetch standings or no data in response.")

    # Test top scorers
    print("\nFetching top scorers...")
    top_scorers_data = client.get_top_scorers(league_id, season_year)
    if top_scorers_data and top_scorers_data.get('response'):
        print(f"Top Scorers fetched for League {league_id}, Season {season_year}.")
        # Further processing of top_scorers_data['response'] could go here
    else:
        print("Failed to fetch top scorers or no data in response.")
