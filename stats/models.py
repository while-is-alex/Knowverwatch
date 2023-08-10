from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    alternate_id = models.IntegerField(
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=4)
    region = models.CharField(
        max_length=200,
        null=True,
        choices=[
            ('W', 'west'),
            ('E', 'east'),
            ('C', 'contenders'),
        ]
    )
    logo = models.URLField()
    icon = models.URLField()
    primary_color = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    secondary_color = models.CharField(
        null=True,
        blank=True,
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
    alternate_id = models.IntegerField(
        null=True,
        blank=True,
    )
    headshot_url = models.URLField(null=True)
    name = models.CharField(max_length=250)
    first_name = models.CharField(
        max_length=200,
        null=True,
    )
    last_name = models.CharField(
        max_length=200,
        null=True,
    )
    role = models.CharField(
        max_length=100,
        null=True
    )
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
    teams = models.JSONField(null=True)
    players = models.JSONField(null=True)
    standings = models.JSONField(null=True)
    first_match = models.DateTimeField(null=True)
    last_match = models.DateTimeField(null=True)
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
    match_url = models.URLField(null=True)
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

    class Meta:
        verbose_name_plural = 'Matches'
