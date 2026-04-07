from django.contrib import admin
from .models import TransferRumour

@admin.register(TransferRumour)
class TransferRumourAdmin(admin.ModelAdmin):
    list_display = ['player_name', 'current_club', 'position', 'age', 'fee', 'likelihood', 'status', 'submitted_by']
    list_filter = ['status', 'position']
    list_editable = ['status']
    search_fields = ['player_name', 'current_club']
    ordering = ['-submitted_at']
