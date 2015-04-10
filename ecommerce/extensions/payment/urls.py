""" Payment-related URLs """
from django.conf.urls import patterns, url

from ecommerce.extensions.payment import views

urlpatterns = patterns(
    '',
    url(r'processors/$', views.ProcessorsListView.as_view(), name='processors_list'),
    url(r'/cybersource/callback/$', views.CybersourceResponseView.as_view(), name='cybersource_callback'),
)
