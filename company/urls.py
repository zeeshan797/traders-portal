from django.urls import path
from .views import CompanySearchView, WatchlistView

urlpatterns = [
    path('search/', CompanySearchView.as_view(), name='company-search'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
]
