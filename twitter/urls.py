from django.conf.urls import patterns, url, include
import os

from django.views.generic import TemplateView
site_media = os.path.join( os.path.dirname(__file__), 'site_media')

from twitter import views
urlpatterns = patterns('',
                      (r'^main/$', 'twitter.views.main_page'),
                      (r'^profile/(\w+)/$', 'twitter.views.user_page'),

                      (r'^connections/(\w+)/$', 'twitter.views.connections_page'),
                      (r'^available_users/(\w+)/$', 'twitter.views.available_users_page'),
                      (r'^user/get/(\w+)/$', 'twitter.views.user_profile'),
                      (r'^unfriend/(\w+)/$', 'twitter.views.unfriend'),
                      (r'^add_friend/(\w+)/$', 'twitter.views.add_friend'),
                      (r'^login/$', 'django.contrib.auth.views.login'),
                      (r'^logout/$', 'twitter.views.logout_page'),
                      (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
{'document_root': site_media}),
                      (r'^register/$', 'twitter.views.register_page'),
                       url(r'^register/success/$', TemplateView.as_view(template_name='registration/register_success.html')),
                       (r'^save/$', 'twitter.views.tweet_save_page'),
                       (r'^create_post/$', 'twitter.views.create_post'),
                       (r'^friend/accept/(\w+)/$', 'twitter.views.friend_accept'),
)
