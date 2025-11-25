"""Core models for the ScoutHub application."""

from django.db import models
from django.contrib.auth.models import User  # Import User model


class Team(models.Model):
    """Represents a football team."""

    api_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=10, unique=False)  # MODIFIED: unique=False
    crest_url = models.URLField(max_length=500, blank=True, null=True)
    founded = models.IntegerField(blank=True, null=True)
    venue_name = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(
        null=True, blank=True
    )  # Team's position in league standings
    points = models.IntegerField(
        null=True, blank=True
    )  # Team's points in league standings
    form = models.CharField(
        max_length=5, null=True, blank=True
    )  # Team's recent form (e.g., WWLDD)

    def __str__(self):
        """Return a string representation of the team."""
        return self.name


class Player(models.Model):
    """Represents a football player."""

    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    nationality = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    class Meta:
        """Metaclass for the Player model."""

        unique_together = (
            "name",
            "team",
        )  # A player name should be unique within a team

    def __str__(self):
        """Return a string representation of the player."""
        return f"{self.name} ({self.team.short_name})"


class Report(models.Model):
    """Represents a scouting report created by a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField(max_length=255)
    content = models.TextField()
    teams = models.ManyToManyField(Team, related_name="reports")
    players = models.ManyToManyField(Player, related_name="reports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        """Return a string representation of the report."""
        return f"Report by {self.user.username}: {self.title}"


class LastAPICall(models.Model):  # NEW MODEL
    """
    Records the last time a specific API endpoint was called.

    This is to help manage API rate limits.
    """

    endpoint_type = models.CharField(
        max_length=50, help_text="e.g., 'standings', 'top_scorers'"
    )
    league_id = models.IntegerField()
    season_year = models.IntegerField()
    last_call_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        """Metaclass for the LastAPICall model."""

        unique_together = (
            "endpoint_type",
            "league_id",
            "season_year",
        )
        verbose_name = "Last API Call"
        verbose_name_plural = "Last API Calls"

    def __str__(self):
        """Return a string representation of the LastAPICall record."""
        return (
            f"{self.endpoint_type} for League {self.league_id} in "
            f"{self.season_year} last called at {self.last_call_timestamp}"
        )
