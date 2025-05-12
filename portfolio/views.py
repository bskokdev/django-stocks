from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import Stock, Portfolio, Holding, Transaction, Dividend, Watchlist
from .forms import StockForm, StockSearchForm, PortfolioForm, TransactionForm, WatchlistForm, Stock

@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    watchlists = Watchlist.objects.filter(user=request.user)
    
    # Calculate total portfolio value
    total_value = sum(portfolio.total_value() for portfolio in portfolios)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        portfolio__user=request.user
    ).order_by('-transaction_date')[:5]
    
    context = {
        'portfolios': portfolios,
        'watchlists': watchlists,
        'total_value': total_value,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'dashboard.html', context)

class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stocks'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = StockSearchForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['symbol']:
                queryset = queryset.filter(symbol__icontains=form.cleaned_data['symbol'])
            if form.cleaned_data['name']:
                queryset = queryset.filter(name__icontains=form.cleaned_data['name'])
            if form.cleaned_data['sector']:
                queryset = queryset.filter(sector__icontains=form.cleaned_data['sector'])
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = StockSearchForm(self.request.GET)
        return context

class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock_detail.html'
    context_object_name = 'stock'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dividends'] = Dividend.objects.filter(stock=self.object).order_by('-payment_date')
        return context

class PortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = 'portfolio_list.html'
    context_object_name = 'portfolios'
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = Portfolio
    template_name = 'portfolio_detail.html'
    context_object_name = 'portfolio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.object
        holdings = portfolio.holding_set.all()
        
        # Performance metrics
        total_invested = sum(holding.shares * holding.average_cost for holding in holdings)
        total_value = sum(holding.current_value() for holding in holdings)
        total_pl = total_value - total_invested
        
        context.update({
            'holdings': holdings,
            'total_invested': total_invested,
            'total_value': total_value,
            'total_pl': total_pl,
            'transactions': Transaction.objects.filter(portfolio=portfolio).order_by('-transaction_date'),
        })
        return context

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    
    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user).order_by('-transaction_date')


@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('/portfolios')
    else:
        form = PortfolioForm()
    
    return render(request, 'portfolio_create.html', {'form': form})

@login_required
def portfolio_update(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            return redirect('/portfolios', pk=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)

    context = {
        'form': form,
        'title': f'Edit {portfolio.name}',
        'action': 'Update',
        'portfolio': portfolio
    }
    return render(request, 'portfolio_form.html', context)

@login_required
def portfolio_delete(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        return redirect('/portfolios')

    return render(request, 'portfolio_confirm_delete.html', {
        'portfolio': portfolio
    })

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)  # Pass user to form
        if form.is_valid():
            transaction = form.save()
            portfolio = transaction.portfolio
            stock = transaction.stock
            holding, created = Holding.objects.get_or_create(
                portfolio=portfolio,
                stock=stock,
                defaults={'shares': 0, 'average_cost': 0}
            )
            if transaction.transaction_type == Transaction.BUY:
                total_shares = holding.shares + transaction.shares
                total_cost = (holding.shares * holding.average_cost) + (transaction.shares * transaction.price_per_share)
                holding.average_cost = total_cost / total_shares if total_shares > 0 else 0
                holding.shares = total_shares
            else:  # SELL
                holding.shares -= transaction.shares
                if holding.shares <= 0:
                    holding.delete()
                    return redirect('/portfolios/', pk=portfolio.pk)
            holding.save()
            return redirect('/portfolios', pk=portfolio.pk)
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'transaction_create.html', {'form': form})

class WatchlistListView(LoginRequiredMixin, ListView):
    model = Watchlist
    template_name = 'watchlist_list.html'
    context_object_name = 'watchlists'
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

class WatchlistDetailView(LoginRequiredMixin, DetailView):
    model = Watchlist
    template_name = 'watchlist_detail.html'
    context_object_name = 'watchlist'

@login_required
def stock_create(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/stocks')
    else:
        form = StockForm()
    return render(request, 'stock_create.html', {'form': form})

@login_required
def stock_update(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('/stocks', pk=stock.pk)
    else:
        form = StockForm(instance=stock)
    
    return render(request, 'stock_form.html', {
        'form': form,
        'title': f'Edit {stock.symbol}',
        'action': 'Update',
        'stock': stock
    })

@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        return redirect('/stocks')
    return render(request, 'stock_confirm_delete.html', {'stock': stock})

@login_required
def watchlist_create(request):
    if request.method == 'POST':
        form = WatchlistForm(request.POST)
        if form.is_valid():
            watchlist = form.save(commit=False)
            watchlist.user = request.user
            watchlist.save()
            form.save_m2m()
            return redirect('/watchlists')
    else:
        form = WatchlistForm()
    
    return render(request, 'watchlist_create.html', {'form': form})

@login_required
def watchlist_update(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WatchlistForm(request.POST, instance=watchlist)
        if form.is_valid():
            watchlist = form.save()
            return redirect('/watchlists', pk=watchlist.pk)
    else:
        form = WatchlistForm(instance=watchlist)
    context = {
        'form': form,
        'title': f'Edit {watchlist.name}',
        'action': 'Update',
        'watchlist': watchlist
    }
    return render(request, 'watchlist_form.html', context)

@login_required
def watchlist_delete(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    if request.method == 'POST':
        watchlist.delete()
        return redirect('/watchlists')

    return render(request, 'watchlist_confirm_delete.html', {
        'watchlist': watchlist
    })

class DividendListView(LoginRequiredMixin, ListView):
    model = Dividend
    template_name = 'dividend_list.html'
    context_object_name = 'dividends'
    
    def get_queryset(self):
        return Dividend.objects.filter(stock__holding__portfolio__user=self.request.user).distinct().order_by('-payment_date')

@login_required
def performance(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    
    # Calculate performance metrics for each portfolio
    portfolio_data = []
    for portfolio in portfolios:
        holdings = portfolio.holding_set.all()
        total_invested = sum(holding.shares * holding.average_cost for holding in holdings)
        total_value = sum(holding.current_value() for holding in holdings)
        total_pl = total_value - total_invested
        pl_percent = (total_pl / total_invested * 100) if total_invested > 0 else 0
        
        portfolio_data.append({
            'portfolio': portfolio,
            'total_invested': total_invested,
            'total_value': total_value,
            'total_pl': total_pl,
            'pl_percent': pl_percent,
        })
    
    # Calculate overall performance
    overall_invested = sum(data['total_invested'] for data in portfolio_data)
    overall_value = sum(data['total_value'] for data in portfolio_data)
    overall_pl = overall_value - overall_invested
    overall_pl_percent = (overall_pl / overall_invested * 100) if overall_invested > 0 else 0
    
    context = {
        'portfolio_data': portfolio_data,
        'overall_invested': overall_invested,
        'overall_value': overall_value,
        'overall_pl': overall_pl,
        'overall_pl_percent': overall_pl_percent,
    }
    return render(request, 'performance.html', context)

# API
@login_required
@require_GET
def api_stocks(request):
    stocks = Stock.objects.all()
    data = [{
        'symbol': stock.symbol,
        'name': stock.name,
        'sector': stock.sector,
        'industry': stock.industry,
        'current_price': str(stock.current_price),
        'last_updated': stock.last_updated.isoformat(),
    } for stock in stocks]
    return JsonResponse({'stocks': data})

@login_required
@require_GET
def api_portfolios(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    data = [{
        'id': portfolio.id,
        'name': portfolio.name,
        'description': portfolio.description,
        'created_at': portfolio.created_at.isoformat(),
        'updated_at': portfolio.updated_at.isoformat(),
        'total_value': str(portfolio.total_value()),
    } for portfolio in portfolios]
    return JsonResponse({'portfolios': data})

@login_required
@require_GET
def api_holdings(request, portfolio_id):
    holdings = Holding.objects.filter(portfolio_id=portfolio_id, portfolio__user=request.user)
    data = [{
        'stock_symbol': holding.stock.symbol,
        'stock_name': holding.stock.name,
        'shares': str(holding.shares),
        'average_cost': str(holding.average_cost),
        'current_price': str(holding.stock.current_price),
        'current_value': str(holding.current_value()),
        'profit_loss': str(holding.profit_loss()),
        'profit_loss_percent': str(holding.profit_loss_percent()),
    } for holding in holdings]
    return JsonResponse({'holdings': data})

@login_required
@require_GET
def api_transactions(request, portfolio_id):
    transactions = Transaction.objects.filter(portfolio_id=portfolio_id, portfolio__user=request.user)
    data = [{
        'id': transaction.id,
        'stock_symbol': transaction.stock.symbol,
        'transaction_type': transaction.transaction_type,
        'shares': str(transaction.shares),
        'price_per_share': str(transaction.price_per_share),
        'commission': str(transaction.commission),
        'total_cost': str(transaction.total_cost()),
        'transaction_date': transaction.transaction_date.isoformat(),
        'notes': transaction.notes,
    } for transaction in transactions]
    return JsonResponse({'transactions': data})

@login_required
@require_GET
def api_dividends(request):
    dividends = Dividend.objects.filter(stock__holding__portfolio__user=request.user).distinct()
    data = [{
        'stock_symbol': dividend.stock.symbol,
        'amount_per_share': str(dividend.amount_per_share),
        'payment_date': dividend.payment_date.isoformat(),
        'record_date': dividend.record_date.isoformat(),
        'declared_date': dividend.declared_date.isoformat() if dividend.declared_date else None,
    } for dividend in dividends]
    return JsonResponse({'dividends': data})

@login_required
@require_GET
def api_watchlists(request):
    watchlists = Watchlist.objects.filter(user=request.user)
    data = [{
        'id': watchlist.id,
        'name': watchlist.name,
        'created_at': watchlist.created_at.isoformat(),
        'stocks': [{
            'symbol': stock.symbol,
            'name': stock.name,
            'current_price': str(stock.current_price),
        } for stock in watchlist.stocks.all()],
    } for watchlist in watchlists]
    return JsonResponse({'watchlists': data})
