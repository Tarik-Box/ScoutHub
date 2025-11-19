from django.db import models
from django.contrib.auth.models import User # Import User model

class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=10, unique=True)
    crest_url = models.URLField(max_length=500, blank=True, null=True)
    founded = models.IntegerField(blank=True, null=True)
    venue_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    nationality = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'team',) # A player name should be unique within a team

    def __str__(self):
        return f"{self.name} ({self.team.short_name})"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    content = models.TextField()
    teams = models.ManyToManyField(Team, related_name='reports')
    players = models.ManyToManyField(Player, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username}: {self.title}"