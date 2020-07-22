from django.contrib import admin
from .models import User, Auction, Bid, Comment, WatchList, Winner


# Register your models here.


class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction_username', 'name', 'category', 'start_bid', 'datetime')
    sortable_by = ('id', 'auction_username', 'name', 'datetime')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'password')
    sortable_by = ('id', 'username')


class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'auction', 'bid')
    sortable_by = 'auction'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'auction', 'comment')
    sortable_by = ('auction', 'name')


class WatchListAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_user', 'watchlist')


class WinnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction_id', 'auction_won', 'final_bid')


admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(Winner, WinnerAdmin)