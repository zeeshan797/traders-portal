from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Company, Watchlist
from .serializers import CompanySerializer, WatchlistSerializer, AddToWatchlistSerializer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class CompanySearchThrottle(AnonRateThrottle):
    scope = 'company_search'

class WatchlistThrottle(AnonRateThrottle):
    scope = 'watchlist'

class CompanySearchView(APIView):
    throttle_classes = [CompanySearchThrottle]
    """
    Search and filter companies by name or symbol
    GET /api/companies/search/?q=CIPLA
    GET /api/companies/search/?q=reliance
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search by company name or symbol (case-insensitive)
        companies = Company.objects.filter(
            Q(company_name__icontains=query) | Q(symbol__icontains=query)
        ).order_by('company_name')[:50]  # Limit to 50 results for performance
        
        serializer = CompanySerializer(companies, many=True)
        
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })


class WatchlistView(APIView):
    throttle_classes = [WatchlistThrottle]
    """
    Manage user's watchlist
    GET /api/companies/watchlist/ - View watchlist
    POST /api/companies/watchlist/ - Add company
    DELETE /api/companies/watchlist/ - Remove company
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's watchlist"""
        watchlist = Watchlist.objects.filter(user=request.user).select_related('company').order_by('-added_at')
        serializer = WatchlistSerializer(watchlist, many=True)
        
        return Response({
            "count": len(serializer.data),
            "watchlist": serializer.data
        })
    
    def post(self, request):
        """Add company to watchlist"""
        serializer = AddToWatchlistSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        company_id = serializer.validated_data['company_id']
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create watchlist entry (or get if already exists)
        watchlist, created = Watchlist.objects.get_or_create(
            user=request.user,
            company=company
        )
        
        if created:
            return Response(
                {
                    "message": "Company added to watchlist successfully",
                    "company": CompanySerializer(company).data
                }, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "Company is already in your watchlist"}, 
                status=status.HTTP_200_OK
            )
    
    def delete(self, request):
        """Remove company from watchlist"""
        serializer = AddToWatchlistSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        company_id = serializer.validated_data['company_id']
        
        deleted_count, _ = Watchlist.objects.filter(
            user=request.user,
            company_id=company_id
        ).delete()
        
        if deleted_count > 0:
            return Response(
                {"message": "Company removed from watchlist successfully"}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Company not found in your watchlist"}, 
                status=status.HTTP_404_NOT_FOUND
            )

