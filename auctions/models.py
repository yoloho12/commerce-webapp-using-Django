from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Auction(models.Model):
    auction_username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_username")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    image_url = models.CharField(max_length=512, blank=True)
    category = models.CharField(max_length=64, blank=True)
    datetime = models.DateTimeField(auto_created=True)
    start_bid = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return f"{self.name}"


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid")
    bid = models.PositiveIntegerField(default=0, blank=True)
    name = models.CharField(max_length=64, default=None)

    def __str__(self):
        return f"{self.bid}"


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comment")
    comment = models.CharField(max_length=1024, default=None)
    name = models.CharField(max_length=64, default=None)

    def __str__(self):
        return f"{self.comment}"


class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    auction_id = models.IntegerField(default=0)
    auction_won = models.CharField(default=None, max_length=128)
    final_bid = models.IntegerField(default=0)

    def __str__(self):
        return F"{self.auction_id}"


class WatchList(models.Model):
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_user")
    watchlist = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.watchlist}"

