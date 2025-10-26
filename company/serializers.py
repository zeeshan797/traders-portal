from rest_framework import serializers
from .models import Company, Watchlist

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
    
class WatchlistSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    class Meta:
        model = Watchlist
        fields = ['id', 'company', 'added_at']
    
class AddToWatchlistSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    class Meta:
        model = Watchlist
        fields = ['company_id']
