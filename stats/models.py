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
    heroes = models.JSONField(null=True)
    stats = models.JSONField(null=True)
    segment_stats = models.JSONField(null=True)
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
    start_timestamp = models.DateTimeField(null=True)
    end_timestamp = models.DateTimeField(null=True)
    state = models.CharField(max_length=100)
    teams = models.JSONField(null=True)
    games = models.JSONField(null=True)
    players = models.JSONField(null=True)
    winner_id = models.IntegerField(null=True)
    match_url = models.URLField(null=True)
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'Match ID: {self.id} ({self.date})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('match-details-page', args=[self.slug])

    class Meta:
        verbose_name_plural = 'Matches'


class Award(models.Model):
    name = models.CharField(
        max_length=300,
        choices=[
            ('League Champion', 'League Champion'),
            ('MVP', 'MVP'),
            ('Grand Finals MVP', 'Grand Finals MVP'),
            ('Dennis Hawelka Award', 'Dennis Hawelka Award'),
            ('Alarm Rookie of the Year', 'Alarm Rookie of the Year'),
            ('Role Star', 'Role Star'),
        ]
    )
    year = models.IntegerField(null=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='awards',
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='awards',
    )
    slug = models.SlugField(
        default='',
        blank=True,
        null=False,
        db_index=True,
    )

    def __str__(self):
        return f'{self.name} ({self.year})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse('awards-page', args=[self.slug])
