from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Stock URLs
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stocks/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stocks/create/', views.stock_create, name='stock_create'),
    path('stocks/<int:pk>/edit/', views.stock_update, name='stock_update'),
    path('stocks/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    
    # Portfolio URLs
    path('portfolios/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolios/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolios/<int:pk>/edit/', views.portfolio_update, name='portfolio_update'),
    path('portfolios/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),

    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    
    # Watchlist URLs
    path('watchlists/', views.WatchlistListView.as_view(), name='watchlist_list'),
    path('watchlists/<int:pk>/', views.WatchlistDetailView.as_view(), name='watchlist_detail'),
    path('watchlists/create/', views.watchlist_create, name='watchlist_create'),
    path('watchlists/<int:pk>/edit/', views.watchlist_update, name='watchlist_update'),
    path('watchlists/<int:pk>/delete/', views.watchlist_delete, name='watchlist_delete'),

    # Dividend URLs
    path('dividends/', views.DividendListView.as_view(), name='dividend_list'),
    
    # Performance URL
    path('performance/', views.performance, name='performance'),

    # API URLs
    path('api/stocks/', views.api_stocks, name='api_stocks'),
    path('api/portfolios/', views.api_portfolios, name='api_portfolios'),
    path('api/portfolios/<int:portfolio_id>/holdings/', views.api_holdings, name='api_holdings'),
    path('api/portfolios/<int:portfolio_id>/transactions/', views.api_transactions, name='api_transactions'),
    path('api/dividends/', views.api_dividends, name='api_dividends'),
    path('api/watchlists/', views.api_watchlists, name='api_watchlists'),
]
