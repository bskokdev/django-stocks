from django.contrib import admin
from .models import Stock, Portfolio, Holding, Transaction, Dividend, Watchlist

class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'sector', 'industry', 'current_price', 'last_updated')
    search_fields = ('symbol', 'name')
    list_filter = ('sector', 'industry')

class HoldingInline(admin.TabularInline):
    model = Holding
    extra = 0

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)
    inlines = [HoldingInline]

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'transaction_type', 'shares', 'price_per_share', 'transaction_date')
    search_fields = ('stock__symbol', 'portfolio__name')
    list_filter = ('transaction_type', 'portfolio__user')

class DividendAdmin(admin.ModelAdmin):
    list_display = ('stock', 'amount_per_share', 'payment_date', 'record_date')
    search_fields = ('stock__symbol',)
    list_filter = ('payment_date',)

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('stocks',)

admin.site.register(Stock, StockAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Holding)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Dividend, DividendAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
