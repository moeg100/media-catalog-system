from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
import random
import string

class Patron(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    card_number = models.CharField(max_length=20, unique=True)
    pin_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def set_pin(self, pin):
        self.pin_hash = make_password(pin)
    
    def check_pin(self, pin):
        return check_password(pin, self.pin_hash)
    
    @staticmethod
    def generate_card_number():
        return 'LC-' + ''.join(random.choices(string.digits, k=6))
    
    def get_total_fines(self):
        return sum(f.amount for f in self.fine_set.filter(paid=False))
    
    def get_checked_out_count(self):
        return self.checkout_set.filter(returned_at__isnull=True).count()
    
    def get_holds_count(self):
        return self.hold_set.filter(status__in=['pending', 'ready', 'in_transit']).count()
    
    def __str__(self):
        return f"{self.name} ({self.card_number})"

class Librarian(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, password):
        self.password_hash = make_password(password)
    
    def check_password(self, password):
        return check_password(password, self.password_hash)
    
    def __str__(self):
        return self.username

class MediaItem(models.Model):
    TYPE_CHOICES = [
        ('book', 'Book'),
        ('audiobook', 'Audiobook'),
        ('dvd', 'DVD'),
        ('cd', 'Music CD'),
        ('magazine', 'Magazine'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('on_hold', 'On Hold'),
        ('in_transit', 'In Transit'),
        ('lost', 'Lost'),
    ]
    
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    media_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    barcode = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def get_loan_period_days(self):
        if self.media_type in ['dvd', 'cd']:
            return 7
        elif self.media_type == 'magazine':
            return 14
        return 21
    
    def get_fine_per_day(self):
        return 0.45
    
    def __str__(self):
        return f"{self.title} by {self.author}"

class Checkout(models.Model):
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    checked_out_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    renewals = models.IntegerField(default=0)
    
    def is_overdue(self):
        check_time = self.returned_at if self.returned_at else timezone.now()
        return check_time > self.due_date
    
    def days_overdue(self):
        check_time = self.returned_at if self.returned_at else timezone.now()
        if check_time <= self.due_date:
            return 0
        return (check_time - self.due_date).days
    
    def days_until_due(self):
        if self.returned_at:
            return 0
        if timezone.now() > self.due_date:
            return 0
        return (self.due_date - timezone.now()).days
    
    def calculate_fine(self):
        days = self.days_overdue()
        if days <= 0:
            return 0
        return round(days * self.media_item.get_fine_per_day(), 2)
    
    def can_renew(self):
        if self.returned_at:
            return False
        return self.renewals < 2 and timezone.now() <= self.due_date
    
    def renew(self):
        if self.can_renew():
            self.due_date = timezone.now() + timedelta(days=self.media_item.get_loan_period_days())
            self.renewals += 1
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.patron.name} - {self.media_item.title}"

class Hold(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready for Pickup'),
        ('in_transit', 'In Transit'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    queue_position = models.IntegerField(default=1)
    pickup_by = models.DateTimeField(null=True, blank=True)
    pickup_location = models.CharField(max_length=100, default='Main Branch')
    
    def __str__(self):
        return f"Hold: {self.patron.name} - {self.media_item.title}"

class MediaRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    TYPE_CHOICES = [
        ('book', 'Book'),
        ('audiobook', 'Audiobook'),
        ('dvd', 'DVD/Blu-ray'),
        ('cd', 'Music CD'),
        ('magazine', 'Magazine/Journal'),
        ('other', 'Other'),
    ]
    
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True)
    media_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notify_when_available = models.BooleanField(default=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(Librarian, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Request: {self.title} by {self.patron.name}"

class Fine(models.Model):
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Fine: ${self.amount} - {self.patron.name}"

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('checkout', 'Checkout'),
        ('checkin', 'Check In'),
        ('hold_placed', 'Hold Placed'),
        ('hold_cancelled', 'Hold Cancelled'),
        ('request_submitted', 'Request Submitted'),
        ('request_approved', 'Request Approved'),
        ('patron_created', 'Patron Created'),
        ('renewal', 'Renewal'),
    ]
    
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    patron = models.ForeignKey(Patron, on_delete=models.SET_NULL, null=True, blank=True)
    media_item = models.ForeignKey(MediaItem, on_delete=models.SET_NULL, null=True, blank=True)
    librarian = models.ForeignKey(Librarian, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.created_at}"
