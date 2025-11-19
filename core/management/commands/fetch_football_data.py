import datetime
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.api_client import FootballAPIClient
from core.models import Team, Player, LastAPICall

class Command(BaseCommand):
    help = 'Fetches football data (teams and players) from API-Football and updates the database, respecting API rate limits.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--league_id',
            type=int,
            default=39, # English Premier League
            help='ID of the league to fetch data for (default: 39 for EPL).'
        )
        parser.add_argument(
            '--season_year',
            type=int,
            default=timezone.now().year - (1 if timezone.now().month < 8 else 0), # Default to current or previous season
            help='Year of the season to fetch data for (default: current season).'
        )
        parser.add_argument(
            '--force_update',
            action='store_true',
            help='Force API call even if within rate limit period.'
        )

    def handle(self, *args, **options):
        league_id = options['league_id']
        season_year = options['season_year']
        force_update = options['force_update']

        self.stdout.write(self.style.SUCCESS(f"Starting data fetch for League ID: {league_id}, Season: {season_year}"))

        client = FootballAPIClient()

        # Define rate limit period (e.g., 23 hours for a 24-hour limit with some buffer)
        RATE_LIMIT_PERIOD = datetime.timedelta(hours=23)

        # Process Standings (Teams)
        self.fetch_and_process_data(
            client=client,
            endpoint_type='standings',
            fetch_func=client.get_standings,
            process_func=self._process_standings_data,
            league_id=league_id,
            season_year=season_year,
            rate_limit_period=RATE_LIMIT_PERIOD,
            force_update=force_update,
            success_msg="Standings updated successfully.",
            error_msg="Failed to fetch or process standings data."
        )

        # Process Top Scorers (Players)
        self.fetch_and_process_data(
            client=client,
            endpoint_type='top_scorers',
            fetch_func=client.get_top_scorers,
            process_func=self._process_top_scorers_data,
            league_id=league_id,
            season_year=season_year,
            rate_limit_period=RATE_LIMIT_PERIOD,
            force_update=force_update,
            success_msg="Top scorers updated successfully.",
            error_msg="Failed to fetch or process top scorers data."
        )

        self.stdout.write(self.style.SUCCESS('Data fetching process completed.'))

    def fetch_and_process_data(self, client, endpoint_type, fetch_func, process_func, league_id, season_year, rate_limit_period, force_update, success_msg, error_msg):
        self.stdout.write(f"Checking {endpoint_type} update status...")
        last_call_obj, created = LastAPICall.objects.get_or_create(
            endpoint_type=endpoint_type,
            league_id=league_id,
            season_year=season_year,
            defaults={'last_call_timestamp': timezone.now() - rate_limit_period * 2} # Ensure initial fetch
        )

        time_since_last_call = timezone.now() - last_call_obj.last_call_timestamp

        if force_update or time_since_last_call > rate_limit_period:
            self.stdout.write(self.style.WARNING(f"Fetching new {endpoint_type} data from API..."))
            try:
                api_data = fetch_func(league_id, season_year)
                if api_data and api_data.get('response'):
                    process_func(api_data['response'], league_id, season_year)
                    last_call_obj.last_call_timestamp = timezone.now()
                    last_call_obj.save()
                    self.stdout.write(self.style.SUCCESS(success_msg))
                else:
                    self.stdout.write(self.style.ERROR(error_msg + " (API response was empty or malformed)"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred during {endpoint_type} fetch/process: {e}"))
                self.stdout.write(self.style.ERROR(traceback.format_exc())) # Print full traceback for debugging
        else:
            self.stdout.write(self.style.NOTICE(f"{endpoint_type.capitalize()} data recently updated ({time_since_last_call} ago). Skipping API call."))


    @transaction.atomic
    def _process_standings_data(self, data_response, league_id, season_year): # MODIFIED: Added season_year
        # API-Football /standings response structure:
        # data_response = [ { 'league': { 'id': 39, 'name': 'Premier League', ..., 'standings': [ [ { 'rank': 1, 'team': {...} }, ... ] ] } } ]
        
        if not data_response:
            self.stdout.write(self.style.WARNING("No standings data to process."))
            return

        # Assuming we only care about the first league in the response if multiple are returned
        league_info = data_response[0].get('league', {})
        standings = league_info.get('standings', [])
        
        if not standings:
            self.stdout.write(self.style.WARNING("No standings found in API response."))
            return

        # Standings can be grouped (e.g., by group in a cup), but for league, it's usually one list
        for standing_group in standings:
            for team_standing in standing_group:
                team_api_data = team_standing.get('team', {})
                
                team_id_from_api = team_api_data.get('id')
                team_name = team_api_data.get('name')
                team_short_name = team_api_data.get('code') # API-Football v3 often uses 'code' for short name
                team_crest_url = team_api_data.get('logo')

                if team_id_from_api and team_name:
                    team, created = Team.objects.update_or_create(
                        name=team_name,
                        defaults={
                            'short_name': team_short_name if team_short_name else team_name[:10],
                            'crest_url': team_crest_url,
                            # Founded and venue_name are typically not in /standings endpoint
                            # and would require a separate /teams endpoint call for each team_id
                            # For simplicity now, we leave them as null/blank if not found.
                        }
                    )
                    if created:
                        self.stdout.write(f"Created Team: {team.name}")
                    else:
                        self.stdout.write(f"Updated Team: {team.name}")
                else:
                    self.stdout.write(self.style.WARNING(f"Skipping team with incomplete data: {team_api_data}"))


    @transaction.atomic
    def _process_top_scorers_data(self, data_response, league_id, season_year):
        # API-Football /players/topscorers response structure:
        # data_response = [ { 'player': {...}, 'statistics': [ { 'team': {...}, 'league': {...}, 'games': {...} }, ... ] }, ... ]

        if not data_response:
            self.stdout.write(self.style.WARNING("No top scorers data to process."))
            return

        for player_entry in data_response:
            player_api_data = player_entry.get('player', {})
            statistics_list = player_entry.get('statistics', [])
            
            player_id_from_api = player_api_data.get('id')
            player_name = player_api_data.get('name')
            player_nationality = player_api_data.get('nationality')
            player_image_url = player_api_data.get('photo')

            player_dob_str = player_api_data.get('birth', {}).get('date')
            player_dob = None
            if player_dob_str:
                try:
                    player_dob = datetime.datetime.strptime(player_dob_str, '%Y-%m-%d').date()
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Could not parse DOB '{player_dob_str}' for player {player_name}."))
            
            # Find the relevant team from statistics. A player can have stats for multiple teams/leagues/seasons.
            # We need to find the team they are currently playing for in the specified league/season.
            team_obj = None
            current_team_name = None
            player_position = None
            
            for stats in statistics_list:
                team_stats = stats.get('team', {})
                league_stats = stats.get('league', {})
                games_stats = stats.get('games', {})

                if league_stats.get('id') == league_id and league_stats.get('season') == season_year:
                    current_team_name = team_stats.get('name')
                    player_position = games_stats.get('position')
                    break # Found stats for the current league/season

            if current_team_name:
                try:
                    # Retrieve the Team object. We assume teams are already processed from standings.
                    team_obj = Team.objects.get(name=current_team_name)
                except Team.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Team '{current_team_name}' not found in DB for player {player_name}. Skipping player update."))
                    continue
            else:
                self.stdout.write(self.style.WARNING(f"Could not determine current team for player {player_name} in specified league/season. Skipping player update."))
                continue

            if player_id_from_api and player_name and team_obj:
                player, created = Player.objects.update_or_create(
                    name=player_name,
                    team=team_obj,
                    defaults={
                        'nationality': player_nationality,
                        'position': player_position,
                        'date_of_birth': player_dob,
                        'image_url': player_image_url,
                    }
                )
                if created:
                    self.stdout.write(f"Created Player: {player.name} ({player.team.short_name})")
                else:
                    self.stdout.write(f"Updated Player: {player.name} ({player.team.short_name})")
            else:
                self.stdout.write(self.style.WARNING(f"Skipping player with incomplete data: {player_api_data}"))
