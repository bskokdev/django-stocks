from django import forms
from .models import Stock, Portfolio, Transaction, Dividend, Watchlist

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['symbol', 'name', 'sector', 'industry', 'current_price']
        widgets = {
            'symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'current_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def clean_symbol(self):
        symbol = self.cleaned_data['symbol'].upper()
        if self.instance.pk is None:  # Only check for new stocks
            if Stock.objects.filter(symbol=symbol).exists():
                raise forms.ValidationError("A stock with this symbol already exists.")
        return symbol

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['portfolio', 'stock', 'transaction_type', 'shares', 'price_per_share', 'commission', 'transaction_date', 'notes']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'portfolio': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)
        if self.user:
            # Filter portfolios and stocks based on the user
            self.fields['portfolio'].queryset = Portfolio.objects.filter(user=self.user)
            self.fields['stock'].queryset = Stock.objects.all()

class DividendForm(forms.ModelForm):
    class Meta:
        model = Dividend
        fields = ['stock', 'amount_per_share', 'payment_date', 'record_date', 'declared_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'record_date': forms.DateInput(attrs={'type': 'date'}),
            'declared_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name', 'stocks']
        widgets = {
            'stocks': forms.CheckboxSelectMultiple,
        }

class StockSearchForm(forms.Form):
    symbol = forms.CharField(max_length=10, required=False)
    name = forms.CharField(max_length=100, required=False)
    sector = forms.CharField(max_length=50, required=False)
