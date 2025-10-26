from django.db import models

# Create your models here.
from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    scripcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['company_name']),
        ]
        
    def __str__(self):
        return f"{self.symbol} - {self.company_name}"

from django.contrib.auth.models import User

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='watchers')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'company')  # Prevent duplicate entries
        indexes = [
            models.Index(fields=['user', 'company']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.company.symbol}"
