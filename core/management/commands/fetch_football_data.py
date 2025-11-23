import datetime
import time
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.api_client import FootballAPIClient
from core.models import Team, Player, LastAPICall


class Command(BaseCommand):
    """Django management command to fetch football data (teams and players) from API-Football."""

    help = "Fetches football data (teams and players) from API-Football and updates the database, respecting API rate limits."

    def add_arguments(self, parser):
        parser.add_argument(
            "--league_id",
            type=int,
            default=39,  # English Premier League
            help="ID of the league to fetch data for (default: 39 for EPL).",
        )
        parser.add_argument(
            "--season_year",
            type=int,
            default=timezone.now().year
            - (
                1 if timezone.now().month < 8 else 0
            ),  # Default to current or previous season
            help="Year of the season to fetch data for (default: current season).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force API call even if within rate limit period.",
        )

    def handle(self, *args, **options):
        league_id = options["league_id"]
        season_year = options["season_year"]
        force = options["force"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting data fetch for League ID: {league_id}, Season: {season_year}"
            )
        )

        client = FootballAPIClient()
        RATE_LIMIT_PERIOD = datetime.timedelta(hours=23)

        # Step 1: Fetch Standings to ensure teams are in the database
        self.fetch_and_process_data(
            client=client,
            endpoint_type="standings",
            fetch_func=lambda: client.get_standings(league_id, season_year),
            process_func=lambda data: self._process_standings_data(
                data, league_id, season_year
            ),
            league_id=league_id,
            season_year=season_year,
            rate_limit_period=RATE_LIMIT_PERIOD,
            force=force,
            success_msg="Standings updated successfully.",
            error_msg="Failed to fetch or process standings data.",
        )

        # Step 2: Fetch Top Scorers
        self.fetch_and_process_data(
            client=client,
            endpoint_type="topscorers",
            fetch_func=lambda: client.get_top_scorers(league_id, season_year),
            process_func=lambda data: self._process_top_scorers_data(
                data, league_id, season_year
            ),
            league_id=league_id,
            season_year=season_year,
            rate_limit_period=RATE_LIMIT_PERIOD,
            force=force,
            success_msg="Top scorers updated successfully.",
            error_msg="Failed to fetch or process top scorers data.",
        )

        # Step 3: Fetch all players for each team
        self.stdout.write(
            self.style.SUCCESS("\nStarting full player roster fetch for all teams...")
        )
        all_players_endpoint = "all_players_batch"

        last_call_obj, created = LastAPICall.objects.get_or_create(
            endpoint_type=all_players_endpoint,
            league_id=league_id,
            season_year=season_year,
            defaults={"last_call_timestamp": timezone.now() - RATE_LIMIT_PERIOD * 2},
        )

        time_since_last_call = timezone.now() - last_call_obj.last_call_timestamp

        if force or time_since_last_call > RATE_LIMIT_PERIOD:
            self.stdout.write(
                self.style.WARNING(f"Fetching new player rosters from API...")
            )
            teams = Team.objects.all()
            if not teams:
                self.stdout.write(
                    self.style.ERROR(
                        "No teams found in the database. Please fetch standings first."
                    )
                )
                return

            self.stdout.write(
                f"Found {teams.count()} teams. Fetching players for each..."
            )

            for i, team in enumerate(teams):
                self.stdout.write(
                    f"  ({i+1}/{teams.count()}) Fetching players for {team.name} (API ID: {team.api_id})..."
                )
                try:
                    # The actual API call
                    api_data = client.get_players_for_team(
                        team.api_id, league_id, season_year
                    )
                    if api_data and api_data.get("response"):
                        self._process_all_players_data(
                            api_data["response"], team, season_year
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"    No players found in API response for {team.name} or response was empty/malformed."
                            )
                        )

                    # CRITICAL: Wait between requests to respect API rate limits
                    self.stdout.write(f"    Waiting 6 seconds before next request...")
                    time.sleep(6)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"    An error occurred while fetching players for {team.name}: {e}"
                        )
                    )
                    self.stdout.write(self.style.ERROR(traceback.format_exc()))

            # After the loop completes, update the timestamp for the batch operation
            last_call_obj.last_call_timestamp = timezone.now()
            last_call_obj.save()
            self.stdout.write(self.style.SUCCESS("Full player roster fetch completed."))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"Full player roster recently updated ({time_since_last_call} ago). Skipping API calls."
                )
            )

        self.stdout.write(self.style.SUCCESS("\nData fetching process completed."))

        self.stdout.write(self.style.SUCCESS("\nData fetching process completed."))

    def fetch_and_process_data(
        self,
        client,
        endpoint_type,
        fetch_func,
        process_func,
        league_id,
        season_year,
        rate_limit_period,
        force,
        success_msg,
        error_msg,
    ):
        self.stdout.write(f"Checking {endpoint_type} update status...")
        last_call_obj, created = LastAPICall.objects.get_or_create(
            endpoint_type=endpoint_type,
            league_id=league_id,
            season_year=season_year,
            defaults={
                "last_call_timestamp": timezone.now() - rate_limit_period * 2
            },  # Ensure initial fetch
        )

        time_since_last_call = timezone.now() - last_call_obj.last_call_timestamp

        if force or time_since_last_call > rate_limit_period:
            self.stdout.write(
                self.style.WARNING(f"Fetching new {endpoint_type} data from API...")
            )
            try:
                # The fetch_func is now a lambda with pre-set arguments
                api_data = fetch_func()
                if api_data and api_data.get("response"):
                    # The process_func is also a lambda
                    process_func(api_data["response"])
                    last_call_obj.last_call_timestamp = timezone.now()
                    last_call_obj.save()
                    self.stdout.write(self.style.SUCCESS(success_msg))
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            error_msg + " (API response was empty or malformed)"
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An error occurred during {endpoint_type} fetch/process: {e}"
                    )
                )
                self.stdout.write(
                    self.style.ERROR(traceback.format_exc())
                )  # Print full traceback for debugging
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"{endpoint_type.capitalize()} data recently updated ({time_since_last_call} ago). Skipping API call."
                )
            )

    @transaction.atomic
    def _process_standings_data(
        self, data_response, league_id, season_year
    ):  # MODIFIED: Added season_year
        # API-Football /standings response structure:
        # data_response = [ { 'league': { 'id': 39, 'name': 'Premier League', ..., 'standings': [ [ { 'rank': 1, 'team': {...} }, ... ] ] } } ]

        if not data_response:
            self.stdout.write(self.style.WARNING("No standings data to process."))
            return

        # Assuming we only care about the first league in the response if multiple are returned
        league_info = data_response[0].get("league", {})
        standings = league_info.get("standings", [])

        if not standings:
            self.stdout.write(self.style.WARNING("No standings found in API response."))
            return

        # Standings can be grouped (e.g., by group in a cup), but for league, it's usually one list
        for standing_group in standings:
            for team_standing in standing_group:
                team_api_data = team_standing.get("team", {})
                team_position = team_standing.get("rank")
                team_points = team_standing.get("points")
                team_form = team_standing.get("form")

                team_id_from_api = team_api_data.get("id")
                team_name = team_api_data.get("name")
                team_short_name = team_api_data.get(
                    "code"
                )  # API-Football v3 often uses 'code' for short name
                team_crest_url = team_api_data.get("logo")

                if team_id_from_api:
                    team, created = Team.objects.update_or_create(
                        api_id=team_id_from_api,
                        defaults={
                            "name": team_name,
                            "short_name": (
                                team_short_name if team_short_name else team_name[:10]
                            ),
                            "crest_url": team_crest_url,
                            "position": team_position,
                            "points": team_points,
                            "form": team_form,
                        },
                    )
                    if created:
                        self.stdout.write(
                            f"Created Team: {team.name} (API ID: {team.api_id})"
                        )
                    else:
                        self.stdout.write(
                            f"Updated Team: {team.name} (API ID: {team.api_id})"
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping team with incomplete data: {team_api_data}"
                        )
                    )

    @transaction.atomic
    def _process_top_scorers_data(self, data_response, league_id, season_year):
        # API-Football /players/topscorers response structure:
        # data_response = [ { 'player': {...}, 'statistics': [ { 'team': {...}, 'league': {...}, 'games': {...} }, ... ] }, ... ]

        if not data_response:
            self.stdout.write(self.style.WARNING("No top scorers data to process."))
            return

        for player_entry in data_response:
            player_api_data = player_entry.get("player", {})
            statistics_list = player_entry.get("statistics", [])

            player_id_from_api = player_api_data.get("id")
            player_name = player_api_data.get("name")
            player_nationality = player_api_data.get("nationality")
            player_image_url = player_api_data.get("photo")

            player_dob_str = player_api_data.get("birth", {}).get("date")
            player_dob = None
            if player_dob_str:
                try:
                    player_dob = datetime.datetime.strptime(
                        player_dob_str, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not parse DOB '{player_dob_str}' for player {player_name}."
                        )
                    )

            # Find the relevant team from statistics. A player can have stats for multiple teams/leagues/seasons.
            # We need to find the team they are currently playing for in the specified league/season.
            team_obj = None
            current_team_name = None
            player_position = None
            player_goals = 0
            player_assists = 0

            for stats in statistics_list:
                team_stats = stats.get("team", {})
                league_stats = stats.get("league", {})
                games_stats = stats.get("games", {})
                goals_stats = stats.get("goals", {})

                if (
                    league_stats.get("id") == league_id
                    and league_stats.get("season") == season_year
                ):
                    current_team_name = team_stats.get("name")
                    player_position = games_stats.get("position")
                    player_goals = goals_stats.get("total") or 0
                    player_assists = goals_stats.get("assists") or 0
                    break  # Found stats for the current league/season

            if current_team_name:
                try:
                    # Retrieve the Team object. We assume teams are already processed from standings.
                    team_obj = Team.objects.get(name=current_team_name)
                except Team.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Team '{current_team_name}' not found in DB for player {player_name}. Skipping player update."
                        )
                    )
                    continue
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not determine current team for player {player_name} in specified league/season. Skipping player update."
                    )
                )
                continue

            if player_id_from_api and player_name and team_obj:
                player, created = Player.objects.update_or_create(
                    name=player_name,
                    team=team_obj,
                    defaults={
                        "nationality": player_nationality,
                        "position": player_position,
                        "date_of_birth": player_dob,
                        "image_url": player_image_url,
                        "goals": player_goals,
                        "assists": player_assists,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created Player: {player.name} ({player.team.short_name})"
                    )
                else:
                    self.stdout.write(
                        f"Updated Player: {player.name} ({player.team.short_name})"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping player with incomplete data: {player_api_data}"
                    )
                )

    @transaction.atomic
    def _process_all_players_data(self, data_response, team_obj, season_year):
        # API-Football /players response structure is the same as /players/topscorers
        if not data_response:
            self.stdout.write(
                self.style.WARNING(
                    f"No player data to process for team {team_obj.name}."
                )
            )
            return

        for player_entry in data_response:
            player_api_data = player_entry.get("player", {})

            player_id_from_api = player_api_data.get("id")
            player_name = player_api_data.get("name")
            player_nationality = player_api_data.get("nationality")
            player_image_url = player_api_data.get("photo")

            player_dob_str = player_api_data.get("birth", {}).get("date")
            player_dob = None
            if player_dob_str:
                try:
                    player_dob = datetime.datetime.strptime(
                        player_dob_str, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not parse DOB '{player_dob_str}' for player {player_name}."
                        )
                    )

            # In this context, we already have the team object, so we don't need to find it from stats
            # We can find the position from the statistics array
            player_position = None
            statistics_list = player_entry.get("statistics", [])
            for stats in statistics_list:
                if stats.get("league", {}).get("season") == season_year:
                    player_position = stats.get("games", {}).get("position")
                    break

            if player_id_from_api and player_name and team_obj:
                player, created = Player.objects.update_or_create(
                    name=player_name,
                    team=team_obj,
                    defaults={
                        "nationality": player_nationality,
                        "position": player_position,
                        "date_of_birth": player_dob,
                        "image_url": player_image_url,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created Player: {player.name} ({player.team.short_name})"
                    )
                else:
                    self.stdout.write(
                        f"Updated Player: {player.name} ({player.team.short_name})"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping player with incomplete data for team {team_obj.name}: {player_api_data}"
                    )
                )
