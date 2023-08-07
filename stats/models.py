from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    alternate_id = models.IntegerField(null=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=4)
    logo = models.URLField()
    icon = models.URLField()
    primary_color = models.CharField(
        null=True,
        max_length=1
    )
    secondary_color = models.CharField(
        null=True,
        max_length=100,
    )
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'{self.name} ({self.code})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('team-details-page', args=[self.slug])


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    alternate_id = models.IntegerField()
    headshot_url = models.URLField()
    name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        related_name='players',
    )
    number = models.IntegerField(null=True)
    all_teams = models.JSONField()
    heroes = models.JSONField()
    stats = models.JSONField()
    segment_stats = models.JSONField()
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'{self.name} ({self.role})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('player-details-page', args=[self.slug])


class Segment(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=250,
    )
    name = models.CharField(max_length=300)
    season = models.IntegerField()
    teams = models.IntegerField(null=True)
    players = models.JSONField(null=True)
    standings = models.JSONField()
    first_match = models.DateTimeField()
    last_match = models.DateTimeField()
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'{self.name} ({self.season})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('segment-details-page', args=[self.slug])


class Match(models.Model):
    id = models.IntegerField(primary_key=True)
    season = models.IntegerField()
    segment = models.ForeignKey(
        Segment,
        on_delete=models.SET_NULL,
        null=True,
        related_name='matches',
    )
    date = models.DateField()
    state = models.CharField(max_length=100)
    teams = models.JSONField()
    games = models.JSONField()
    players = models.JSONField()
    winner_id = models.IntegerField(null=True)
    match_url = models.URLField()
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'{self.teams} ({self.date})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('match-details-page', args=[self.slug])
