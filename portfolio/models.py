from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50, blank=True, null=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    def total_value(self):
        holdings = self.holding_set.all()
        return sum(holding.current_value() for holding in holdings)

class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    average_cost = models.DecimalField(max_digits=15, decimal_places=6, default=0)

    def current_value(self):
        return self.shares * self.stock.current_price

    def profit_loss(self):
        return (self.stock.current_price - self.average_cost) * self.shares

    def profit_loss_percent(self):
        if self.average_cost == 0:
            return 0
        return ((self.stock.current_price - self.average_cost) / self.average_cost) * 100

    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol}"

class Transaction(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRANSACTION_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    shares = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(0)])
    price_per_share = models.DecimalField(max_digits=15, decimal_places=6)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_date = models.DateTimeField()
    notes = models.TextField(blank=True)

    def total_cost(self):
        return (self.shares * self.price_per_share) + self.commission

    def __str__(self):
        return f"{self.transaction_type} {self.shares} {self.stock.symbol} @ {self.price_per_share}"

class Dividend(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount_per_share = models.DecimalField(max_digits=10, decimal_places=6)
    payment_date = models.DateField()
    record_date = models.DateField()
    declared_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.stock.symbol} dividend {self.amount_per_share} on {self.payment_date}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    stocks = models.ManyToManyField(Stock, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"
