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

    def __str__(self):
        return self.name


class Player(models.Model):
    """Represents a football player."""

    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    nationality = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        unique_together = (
            "name",
            "team",
        )  # A player name should be unique within a team

    def __str__(self):
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
        return f"Report by {self.user.username}: {self.title}"


class LastAPICall(models.Model):  # NEW MODEL
    """
    Records the last time a specific API endpoint was called for a given resource
    to help manage API rate limits.
    """

    endpoint_type = models.CharField(
        max_length=50, help_text="e.g., 'standings', 'top_scorers'"
    )
    league_id = models.IntegerField()
    season_year = models.IntegerField()
    last_call_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "endpoint_type",
            "league_id",
            "season_year",
        )
        verbose_name = "Last API Call"
        verbose_name_plural = "Last API Calls"

    def __str__(self):
        return f"{self.endpoint_type} for League {self.league_id} in {self.season_year} last called at {self.last_call_timestamp}"
