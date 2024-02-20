
from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    SUIT_CHOICES = [
        ('Spades', 'Spades'),
        ('Hearts', 'Hearts'),
        ('Diamonds', 'Diamonds'),
        ('Clubs', 'Clubs'),
    ]

    RANK_CHOICES = [
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('J', 'J'),
        ('Q', 'Q'),
        ('K', 'K'),
        ('A', 'A'),
    ]

    suit = models.CharField(max_length=2, default='')
    rank = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.rank} of {self.suit}'

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cards = models.ManyToManyField(Card, related_name='players_cards')
    wallet = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Hand(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    # You can add more fields related to the hand if needed

    def __str__(self):
        return f'Hand of {self.player.user.username}'

class Game(models.Model):
    current_player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    pot = models.IntegerField(default=0)

    def __str__(self):
        return f'Game: {self.id}'
