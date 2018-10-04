from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from django.template import RequestContext
from forms import *
from models import Tweets, Connections, Invitation
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
def main_page(request):
    if 'invitation' in request.session:
        invitation = Invitation.objects.get(id=request.session['invitation'])
        friendship = Connections(connector_id=invitation.sender.id,connection_id=request.user.id,connection_type=1)
        friendship.save()
        friendship = Connections(connector_id=request.user.id,connection_id=invitation.sender.id, connection_type=1)
        friendship.save()
        invitation.delete()
        del request.session['invitation']
    variables = RequestContext(request, {'users': User.objects.all(), 'current_user': request.user.username})
    return render_to_response(
'main_page.html', variables
)

def user_page(request,username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('Requested user not found.')
    tweets = user.tweets_set.all()
    variables = RequestContext(request, {
'username': username,
'tweets': tweets
})
    return render_to_response('profile.html', variables)

def user_profile(request,username):
    try:
        flag= ""
        user = User.objects.get(username=username)
        connection_set = Connections.objects.filter(connection_id=user.id)
        for connection in connection_set:
            if connection.connector_id == request.user.id:
                flag = "True"
    except User.DoesNotExist:
        raise Http404('Requested user not found.')
    tweets = user.tweets_set.all()
    variables = RequestContext(request, {
'username': username,
'tweets': tweets,
'flag': flag
})
    return render_to_response('user_profile.html', variables)

def connections_page(request,username):
    user = User.objects.get(username=username)
    connection = Connections.objects.filter(connector_id= user.id)
    variables = RequestContext(request, {'username':username, 'connections': connection, 'users': User.objects.all()})
    return render_to_response('user_connections.html',variables)

def add_friend(request,username):
    user = User.objects.get(username=username)
    invitation = Invitation(name = user.username, email= user.email, code= User.objects.make_random_password(20),sender=request.user)
    invitation.save()
    invitation.send()
    connection = Connections.objects.filter(connector_id= user.id)
    variables = RequestContext(request, {'username':username, 'connections': connection, 'users': User.objects.all()})
    return render_to_response('user_connections.html',variables)

def unfriend(request,username):
    user = User.objects.get(username=username)
    connection_set = Connections.objects.filter(connector_id=user.id)
    for connection in connection_set:
            if connection.connection_id == request.user.id:
                connection.delete()
    connection_set = Connections.objects.filter(connector_id=request.user.id)
    for connection in connection_set:
            if connection.connection_id == user.id:
                connection.delete()

    connection = Connections.objects.filter(connector_id= user.id)
    variables = RequestContext(request, {'username':username, 'connections': connection, 'users': User.objects.all()})
    return render_to_response('user_connections.html',variables)

def friend_accept(request, code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id

    return HttpResponseRedirect('/twitter/login/')

def available_users_page(request,username):
    user = User.objects.get(username=username)
    connection = Connections.objects.filter(connector_id= user.id)

    variables = RequestContext(request, {'username':username, 'users': User.objects.all(),'connections': connection, 'id':user.id})
    return render_to_response('available_users.html',variables)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/twitter/login/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )

        return HttpResponseRedirect('/twitter/register/success/')
    else:
        form = RegistrationForm()
        variables = RequestContext(request, {
'form': form
})
    return render_to_response(
'registration/register.html',
variables
)

@login_required
def tweet_save_page(request):
    if request.method == 'POST':
        form = TweetSaveForm(request.POST)
        if form.is_valid():
            tweet = _tweet_save(request, form)
        return HttpResponseRedirect(
'twitter/user/%s/' % request.user.username
)
    else:
        user= User.objects.get(username=request.user.username)
        tweets = user.tweets_set.all()
        form = TweetSaveForm()
        variables = RequestContext(request, {
'form': form,
 'username': request.user.username,
 'tweets': tweets
})
    return render_to_response('user_page.html', variables)

def _tweet_save(request, form):
    tweet= Tweets.objects.create(
user=request.user,
tweet = form.cleaned_data['tweet']
)
    tweet.save()
    return tweet

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        post_text = request.POST.get('the_post')
        response_data = {}

        post = Tweets(tweet=post_text, user_id=request.user.id)
        post.save()

        response_data['result'] = 'Create post successful!'
        response_data['postpk'] = post.pk
        response_data['text'] = post.tweet


        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )
