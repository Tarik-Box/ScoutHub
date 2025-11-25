"""Client for interacting with the API-Football."""
import os
import requests
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
        self.api_host = "v3.football.api-sports.io"

        if not self.api_key:
            raise ValueError(
                "API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )

        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request to {url} failed: {e}")
            return None

    def get_standings(self, league_id, season_year):
        """
        Fetches league standings for a specific league and season.

        Args:
            league_id (int): The ID of the league.
            season_year (int): The year of the season.

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

    def get_players_for_team(self, team_id, league_id, season_year):
        """
        Fetches all players for a specific team, league, and season.

        Args:
            team_id (int): The ID of the team.
            league_id (int): The ID of the league.
            season_year (int): The year of the season.

        Returns:
            dict: JSON data for the team's players, or None.
        """
        endpoint = "/players"
        params = {"team": team_id, "league": league_id, "season": season_year}
        return self._make_request(endpoint, params)
