from typing import List, Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from datetime import datetime

from .models import User, Auction, Bid, WatchList, Comment, Winner


class CreateForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea())
    img_url = forms.CharField(required=False)
    category = forms.CharField()
    start_bid = forms.IntegerField()


def watchListCount(user_id):
    try:
        count = WatchList.objects.filter(current_user = user_id).count
    except WatchList.DoesNoExist:
        count = 0
    return count


@login_required(login_url="login")
def index(request):
    auction_list = Auction.objects.all()
    count = watchListCount(request.user.pk)
    return render(request, "auctions/index.html", {"auction_list": auction_list, "cnt": count, "img_flag": False})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def listing(request, auction_id):

    auction = get_object_or_404(Auction, pk=auction_id)
    bid = Bid.objects.filter(auction=auction_id).order_by('-bid').first()
    highest_bid = str(bid)
    bid_count = auction.bid.count()
    count = watchListCount(request.user.pk)
    close = False
    if str(auction.auction_username) == str(request.user):
        close = True

    if bid is None:
        name = ''
    else:
        name = bid.name

    try:
        onWatch = WatchList.objects.get(watchlist=auction, current_user=request.user)
    except WatchList.DoesNotExist:
        onWatch = False

    if request.method == 'POST':
        if request.POST.get('button') == "comment":
            comment = request.POST.get('comment')
            if comment:
                commentObj = Comment(auction=auction, name=request.user, comment=comment)
                commentObj.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'auction_id': auction.pk}))

        if request.POST.get('button') == "watch":
            newItem = WatchList(watchlist=auction, current_user=request.user)
            newItem.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'auction_id': auction.pk}))

        if request.POST.get('button') == "unwatch":
            watchedItem = WatchList.objects.get(watchlist=auction, current_user=request.user)
            WatchList.delete(watchedItem)
            return HttpResponseRedirect(reverse('listing', kwargs={'auction_id': auction.pk}))

        if request.POST.get('button') == "close":
            # TODO - record username and number
            user1 = User.objects.get(username=name)
            if Bid.objects.filter(auction=auction_id).__len__() == 1:
                Auction.delete(Auction.objects.get(id = auction_id))
                return HttpResponseRedirect(reverse('index'))
            if highest_bid != "None":
                winner = Winner(user=user1, auction_id=auction_id, auction_won=auction.name, final_bid=int(bid.__str__()))
                winner.save()
            Auction.delete(Auction.objects.get(pk=auction_id))
            return HttpResponseRedirect(reverse('index'))

        if request.POST.get('button') == "place":
            if request.POST.get('input_bid') == '':
                return render(request, "auctions/listings.html",
                              {"auction": auction, "close": close, "bid_count": bid_count,
                               "highest_bid": highest_bid, "name": name, "error": "Bid value must be not be empty!",
                               "onWatch": onWatch,"cnt": count})
            input_bid = int(request.POST.get('input_bid'))
            if highest_bid == "None":
                highest_bid = auction.start_bid
            if input_bid < int(highest_bid):
                return render(request, "auctions/listings.html",
                       {"auction": auction, "close": close, "bid_count": bid_count,
                        "highest_bid": highest_bid, "name": name, "error": "Bid value must be higher",
                        "onWatch": onWatch,"cnt": count})

            bidObj = Bid(auction=auction, bid=input_bid, name=request.user.username)
            bidObj.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'auction_id': auction.pk}))

    return render(request, "auctions/listings.html",
                        {"auction": auction, "close": close, "bid_count": bid_count,
                         "highest_bid": highest_bid, "name": name,"onWatch": onWatch,
                         "cnt": count})


@login_required(login_url="login")
def create(request):
    user = User.objects.get(username=request.user)
    count = watchListCount(request.user.pk)
    if request.method == 'POST':
        createdForm = CreateForm(request.POST)
        if createdForm.is_valid():
            name = createdForm.cleaned_data['name']
            description = createdForm.cleaned_data['description']
            img_url = None
            if createdForm.cleaned_data['img_url']:
                img_url = createdForm.cleaned_data['img_url']
            category = createdForm.cleaned_data['category']
            bid = createdForm.cleaned_data['start_bid']
            if bid < 0:
                return render(request, "auctions/create.html",
                              {"form": createdForm, "error": "Bid must be positive value!", "cnt": count})
            if img_url:
                auction = Auction(name=name, auction_username=user, description=description, image_url=img_url,
                                  category=category,start_bid=bid, datetime=datetime.utcnow())
            else:
                auction = Auction(name=name, auction_username=user, start_bid=bid, description=description, category=category,
                                  datetime=datetime.utcnow())

            s_bid = Bid(auction=auction, bid=bid, name=user)
            auction.save()
            s_bid.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'auction_id': auction.pk}))
    else:
        return render(request, "auctions/create.html", {"form": CreateForm, "cnt": count})


@login_required(login_url="login")
def watchlist(request):
    count = watchListCount(request.user.pk)
    user = User.objects.get(username=request.user)
    auction = WatchList.objects.filter(current_user=user.id)
    auction_list = []
    for obj in auction:
        auction_list.append(Auction.objects.get(name=obj))
    return render(request, "auctions/index.html", {"auction_list": auction_list, "cnt": count})


@login_required(login_url="login")
def categories(request):
    auct = Auction.objects.all()
    data = []
    for item in auct:
        if not item.category in data:
            data.append(item.category)
    count = watchListCount(request.user.pk)
    return render(request, "auctions/categories.html", {"cnt": count, "category_list": data})


@login_required(login_url="login")
def categories_view(request, category):
    count = watchListCount(request.user.pk)
    auction = Auction.objects.filter(category=category)
    return render(request, "auctions/index.html", {"auction_list": auction, "cnt": count, "img_flag": True})


def announce(request):
    win_list = Winner.objects.all().order_by('-pk')
    count = watchListCount(request.user.pk)
    return render(request, "auctions/announce.html", {"win_list": win_list, "cnt": count})