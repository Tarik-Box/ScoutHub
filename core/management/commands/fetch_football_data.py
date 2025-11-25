"Management command to fetch and update football data from the API."
import datetime
import time
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.api_client import FootballAPIClient
from core.models import Team, Player, LastAPICall


class Command(BaseCommand):
    """
    Django management command to fetch football data from API-Football.

    This command fetches and updates teams, players, and other related data,
    while respecting the API's rate limits.
    """

    help = (
        "Fetches football data (teams and players) from API-Football and "
        "updates the database, respecting API rate limits."
    )

    def add_arguments(self, parser):
        """Add the command's arguments to the parser."""
        parser.add_argument(
            "--league_id",
            type=int,
            default=39,  # English Premier League
            help="ID of the league to fetch data for (default: 39 for EPL).",
        )
        parser.add_argument(
            "--season_year",
            type=int,
            default=2023,
            help="Year of the season to fetch data for (default: 2023).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force API call even if within rate limit period.",
        )

    def handle(self, *args, **options):
        """Handle the command's execution."""
        league_id = options["league_id"]
        season_year = options["season_year"]
        force = options["force"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting data fetch for League ID: {league_id}, "
                f"Season: {season_year}"
            )
        )

        client = FootballAPIClient()
        rate_limit_period = datetime.timedelta(hours=23)

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
            rate_limit_period=rate_limit_period,
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
            rate_limit_period=rate_limit_period,
            force=force,
            success_msg="Top scorers updated successfully.",
            error_msg="Failed to fetch or process top scorers data.",
        )

        # Step 3: Fetch all players for each team
        self.stdout.write(
            self.style.SUCCESS("\nStarting full player roster fetch for all teams...")
        )
        all_players_endpoint = "all_players_batch"

        last_call_obj, _ = LastAPICall.objects.get_or_create(
            endpoint_type=all_players_endpoint,
            league_id=league_id,
            season_year=season_year,
            defaults={"last_call_timestamp": timezone.now() - rate_limit_period * 2},
        )

        time_since_last_call = timezone.now() - last_call_obj.last_call_timestamp

        if force or time_since_last_call > rate_limit_period:
            self.stdout.write(
                self.style.WARNING("Fetching new player rosters from API...")
            )
            teams = Team.objects.all()
            if not teams:
                self.stdout.write(
                    self.style.ERROR(
                        "No teams found in the database. "
                        "Please fetch standings first."
                    )
                )
                return

            self.stdout.write(
                f"Found {teams.count()} teams. Fetching players for each..."
            )

            for i, team in enumerate(teams):
                self.stdout.write(
                    f"  ({i+1}/{teams.count()}) Fetching players for {team.name} "
                    f"(API ID: {team.api_id})..."
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
                                f"    No players found for {team.name} or "
                                "response was empty/malformed."
                            )
                        )

                    # CRITICAL: Wait between requests to respect API rate limits
                    self.stdout.write("    Waiting 6 seconds before next request...")
                    time.sleep(6)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"    An error occurred while fetching players "
                            f"for {team.name}: {e}"
                        )
                    )
                    self.stdout.write(self.style.ERROR(traceback.format_exc()))

            last_call_obj.last_call_timestamp = timezone.now()
            last_call_obj.save()
            self.stdout.write(self.style.SUCCESS("Full player roster fetch completed."))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"Full player roster recently updated "
                    f"({time_since_last_call} ago). Skipping API calls."
                )
            )

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
        """Wrap the fetch, process, and rate-limiting logic for an endpoint."""
        self.stdout.write(f"Checking {endpoint_type} update status...")
        last_call_obj, _ = LastAPICall.objects.get_or_create(
            endpoint_type=endpoint_type,
            league_id=league_id,
            season_year=season_year,
            defaults={"last_call_timestamp": timezone.now() - rate_limit_period * 2},
        )

        time_since_last_call = timezone.now() - last_call_obj.last_call_timestamp

        if force or time_since_last_call > rate_limit_period:
            self.stdout.write(
                self.style.WARNING(f"Fetching new {endpoint_type} data from API...")
            )
            try:
                api_data = fetch_func()
                if api_data and api_data.get("response"):
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
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"{endpoint_type.capitalize()} data recently updated "
                    f"({time_since_last_call} ago). Skipping API call."
                )
            )

    @transaction.atomic
    def _process_standings_data(self, data_response, league_id, season_year):
        """Process standings data and update Team models."""
        if not data_response:
            self.stdout.write(self.style.WARNING("No standings data to process."))
            return

        league_info = data_response[0].get("league", {})
        standings = league_info.get("standings", [])

        if not standings:
            self.stdout.write(self.style.WARNING("No standings found in API response."))
            return

        for standing_group in standings:
            for team_standing in standing_group:
                team_api_data = team_standing.get("team", {})
                team_position = team_standing.get("rank")
                team_points = team_standing.get("points")
                team_form = team_standing.get("form")

                team_id_from_api = team_api_data.get("id")
                team_name = team_api_data.get("name")
                team_short_name = team_api_data.get("code")
                team_crest_url = team_api_data.get("logo")

                if team_id_from_api:
                    team, created = Team.objects.update_or_create(
                        name=team_name,
                        defaults={
                            "api_id": team_id_from_api,
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
        """Process top scorers data and update Player models."""
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
                            f"Could not parse DOB '{player_dob_str}' "
                            f"for player {player_name}."
                        )
                    )

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
                    break

            if current_team_name:
                try:
                    team_obj = Team.objects.get(name=current_team_name)
                except Team.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Team '{current_team_name}' not found in DB for "
                            f"player {player_name}. Skipping player update."
                        )
                    )
                    continue
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Could not determine current team for player "
                        f"{player_name} in specified league/season. "
                        "Skipping player update."
                    )
                )
                continue

            if player_id_from_api and player_name and team_obj:
                _, created = Player.objects.update_or_create(
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
                        f"Created Player: {player_name} ({team_obj.short_name})"
                    )
                else:
                    self.stdout.write(
                        f"Updated Player: {player_name} ({team_obj.short_name})"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping player with incomplete data: {player_api_data}"
                    )
                )

    @transaction.atomic
    def _process_all_players_data(self, data_response, team_obj, season_year):
        """Process player data for a single team and update Player models."""
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
                            f"Could not parse DOB '{player_dob_str}' "
                            f"for player {player_name}."
                        )
                    )

            player_position = None
            statistics_list = player_entry.get("statistics", [])
            for stats in statistics_list:
                if stats.get("league", {}).get("season") == season_year:
                    player_position = stats.get("games", {}).get("position")
                    break

            if player_id_from_api and player_name and team_obj:
                _, created = Player.objects.update_or_create(
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
                        f"Created Player: {player_name} ({team_obj.short_name})"
                    )
                else:
                    self.stdout.write(
                        f"Updated Player: {player_name} ({team_obj.short_name})"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping player with incomplete data for "
                        f"team {team_obj.name}: {player_api_data}"
                    )
                )