from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from functools import wraps
from .models import Patron, Librarian, MediaItem, Checkout, Hold, MediaRequest, Fine, ActivityLog

def patron_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'patron_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def librarian_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'librarian_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    media_items = MediaItem.objects.all()[:15]
    return render(request, 'main/index.html', {'media_items': media_items})

def login_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'patron':
            card_number = request.POST.get('card_number')
            pin = request.POST.get('pin')
            try:
                patron = Patron.objects.get(card_number=card_number)
                if patron.check_pin(pin):
                    request.session['patron_id'] = patron.id
                    request.session['user_type'] = 'patron'
                    messages.success(request, f'Welcome back, {patron.name}!')
                    return redirect('patron_dashboard')
                else:
                    messages.error(request, 'Invalid PIN.')
            except Patron.DoesNotExist:
                messages.error(request, 'Library card not found.')
        
        elif user_type == 'librarian':
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                librarian = Librarian.objects.get(username=username)
                if librarian.check_password(password):
                    request.session['librarian_id'] = librarian.id
                    request.session['user_type'] = 'librarian'
                    messages.success(request, f'Welcome back, {librarian.username}!')
                    return redirect('librarian_dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except Librarian.DoesNotExist:
                messages.error(request, 'Username not found.')
    
    return render(request, 'main/login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('index')

def patron_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        pin = request.POST.get('pin')
        confirm_pin = request.POST.get('confirm_pin')
        
        if pin != confirm_pin:
            messages.error(request, 'PINs do not match.')
            return render(request, 'main/patron-signup.html')
        
        if Patron.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'main/patron-signup.html')
        
        patron = Patron(
            name=name,
            email=email,
            card_number=Patron.generate_card_number(),
            expires_at=timezone.now() + timedelta(days=365)
        )
        patron.set_pin(pin)
        patron.save()
        
        messages.success(request, f'Account created! Your library card number is {patron.card_number}')
        return redirect('login')
    
    return render(request, 'main/patron-signup.html')

def librarian_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/librarian-signup.html')
        
        if Librarian.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'main/librarian-signup.html')
        
        librarian = Librarian(username=username, email=email)
        librarian.set_password(password)
        librarian.save()
        
        messages.success(request, 'Account created! Please login.')
        return redirect('login')
    
    return render(request, 'main/librarian-signup.html')

@patron_required
def patron_dashboard(request):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    checkouts = Checkout.objects.filter(patron=patron, returned_at__isnull=True)
    holds = Hold.objects.filter(patron=patron, status__in=['pending', 'ready', 'in_transit'])
    fines = Fine.objects.filter(patron=patron, paid=False)
    total_fines = sum(f.amount for f in fines)
    
    due_soon = checkouts.filter(due_date__lte=timezone.now() + timedelta(days=3), due_date__gt=timezone.now()).count()
    ready_for_pickup = holds.filter(status='ready').count()
    
    recent_activity = ActivityLog.objects.filter(patron=patron)[:5]
    
    return render(request, 'patron/patron-dashboard.html', {
        'patron': patron,
        'checkouts_count': checkouts.count(),
        'holds_count': holds.count(),
        'total_fines': total_fines,
        'due_soon': due_soon,
        'ready_for_pickup': ready_for_pickup,
        'recent_activity': recent_activity,
    })

@patron_required
def patron_search(request):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    query = request.GET.get('q', '')
    media_type = request.GET.get('type', '')
    genre = request.GET.get('genre', '')
    search_by = request.GET.get('search_by', 'title')
    
    items = MediaItem.objects.all()
    
    if query:
        if search_by == 'title':
            items = items.filter(title__icontains=query)
        elif search_by == 'author':
            items = items.filter(author__icontains=query)
        elif search_by == 'isbn':
            items = items.filter(isbn__icontains=query)
        elif search_by == 'publisher':
            items = items.filter(publisher__icontains=query)
        else:
            items = items.filter(Q(title__icontains=query) | Q(author__icontains=query))
    
    if media_type:
        items = items.filter(media_type=media_type)
    
    if genre:
        items = items.filter(genre__icontains=genre)
    
    return render(request, 'patron/patron-search.html', {
        'patron': patron,
        'items': items[:24],
        'query': query,
        'media_type': media_type,
        'genre': genre,
        'search_by': search_by,
        'total_count': items.count(),
    })

@patron_required
def patron_checked_out(request):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    checkouts = Checkout.objects.filter(patron=patron, returned_at__isnull=True).select_related('media_item')
    
    due_soon = [c for c in checkouts if 0 < c.days_until_due() <= 3]
    
    return render(request, 'patron/patron-checked-out.html', {
        'patron': patron,
        'checkouts': checkouts,
        'due_soon_count': len(due_soon),
    })

@patron_required
def patron_renew(request, checkout_id):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    checkout = get_object_or_404(Checkout, id=checkout_id, patron=patron)
    
    if checkout.renew():
        ActivityLog.objects.create(
            action='renewal',
            patron=patron,
            media_item=checkout.media_item,
            description=f'Renewed "{checkout.media_item.title}"'
        )
        messages.success(request, f'Successfully renewed "{checkout.media_item.title}"')
    else:
        messages.error(request, 'Cannot renew this item.')
    
    return redirect('patron_checked_out')

@patron_required
def patron_holds(request):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    active_holds = Hold.objects.filter(patron=patron, status__in=['pending', 'ready', 'in_transit']).select_related('media_item')
    hold_history = Hold.objects.filter(patron=patron, status__in=['picked_up', 'cancelled', 'expired']).select_related('media_item')[:10]
    
    return render(request, 'patron/patron-holds.html', {
        'patron': patron,
        'active_holds': active_holds,
        'hold_history': hold_history,
    })

@patron_required
def patron_place_hold(request, item_id):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    media_item = get_object_or_404(MediaItem, id=item_id)
    
    existing_hold = Hold.objects.filter(patron=patron, media_item=media_item, status__in=['pending', 'ready', 'in_transit']).exists()
    if existing_hold:
        messages.error(request, 'You already have a hold on this item.')
        return redirect('patron_search')
    
    queue_position = Hold.objects.filter(media_item=media_item, status='pending').count() + 1
    
    hold = Hold.objects.create(
        patron=patron,
        media_item=media_item,
        queue_position=queue_position
    )
    
    ActivityLog.objects.create(
        action='hold_placed',
        patron=patron,
        media_item=media_item,
        description=f'Placed hold on "{media_item.title}"'
    )
    
    messages.success(request, f'Hold placed on "{media_item.title}". You are #{queue_position} in queue.')
    return redirect('patron_holds')

@patron_required
def patron_cancel_hold(request, hold_id):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    hold = get_object_or_404(Hold, id=hold_id, patron=patron)
    
    hold.status = 'cancelled'
    hold.save()
    
    ActivityLog.objects.create(
        action='hold_cancelled',
        patron=patron,
        media_item=hold.media_item,
        description=f'Cancelled hold on "{hold.media_item.title}"'
    )
    
    messages.success(request, 'Hold cancelled.')
    return redirect('patron_holds')

@patron_required
def patron_requests(request):
    patron = get_object_or_404(Patron, id=request.session['patron_id'])
    
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author', '')
        media_type = request.POST.get('type')
        reason = request.POST.get('reason', '')
        notify = request.POST.get('notify') == 'on'
        
        MediaRequest.objects.create(
            patron=patron,
            title=title,
            author=author,
            media_type=media_type,
            reason=reason,
            notify_when_available=notify
        )
        
        ActivityLog.objects.create(
            action='request_submitted',
            patron=patron,
            description=f'Requested "{title}"'
        )
        
        messages.success(request, 'Request submitted successfully!')
        return redirect('patron_requests')
    
    previous_requests = MediaRequest.objects.filter(patron=patron).order_by('-requested_at')[:10]
    
    return render(request, 'patron/patron-requests.html', {
        'patron': patron,
        'previous_requests': previous_requests,
    })

@librarian_required
def librarian_dashboard(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    
    today = timezone.now().date()
    checkouts_today = Checkout.objects.filter(checked_out_at__date=today).count()
    pending_requests = MediaRequest.objects.filter(status='pending').count()
    overdue_items = Checkout.objects.filter(returned_at__isnull=True, due_date__lt=timezone.now()).count()
    
    recent_activity = ActivityLog.objects.all()[:5]
    
    return render(request, 'librarian/librarian-dashboard.html', {
        'librarian': librarian,
        'checkouts_today': checkouts_today,
        'pending_requests': pending_requests,
        'overdue_items': overdue_items,
        'recent_activity': recent_activity,
    })

@librarian_required
def librarian_catalog(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    query = request.GET.get('q', '')
    media_type = request.GET.get('type', '')
    
    items = MediaItem.objects.all()
    
    if query:
        items = items.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    
    if media_type:
        items = items.filter(media_type=media_type)
    
    return render(request, 'librarian/librarian-catalog.html', {
        'librarian': librarian,
        'items': items[:50],
        'query': query,
        'media_type': media_type,
        'total_count': items.count(),
    })

@librarian_required
def librarian_add_item(request):
    if request.method == 'POST':
        import random
        import string
        
        barcode = 'BC-' + ''.join(random.choices(string.digits, k=9))
        
        MediaItem.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            media_type=request.POST.get('media_type'),
            isbn=request.POST.get('isbn', ''),
            barcode=barcode,
            description=request.POST.get('description', ''),
            genre=request.POST.get('genre', ''),
            publisher=request.POST.get('publisher', ''),
            location=request.POST.get('location', ''),
        )
        
        messages.success(request, 'Item added to catalog.')
        return redirect('librarian_catalog')
    
    return redirect('librarian_catalog')

@librarian_required
def librarian_delete_item(request, item_id):
    item = get_object_or_404(MediaItem, id=item_id)
    title = item.title
    item.delete()
    messages.success(request, f'"{title}" deleted from catalog.')
    return redirect('librarian_catalog')

@librarian_required
def librarian_patrons(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')
    
    patrons = Patron.objects.all()
    
    if query:
        patrons = patrons.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(card_number__icontains=query))
    
    if filter_type == 'active':
        patrons = patrons.filter(status='active')
    elif filter_type == 'expired':
        patrons = patrons.filter(status='expired')
    
    return render(request, 'librarian/librarian-patrons.html', {
        'librarian': librarian,
        'patrons': patrons[:50],
        'query': query,
        'filter_type': filter_type,
        'total_count': patrons.count(),
    })

@librarian_required
def librarian_checkout(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    
    if request.method == 'POST':
        patron_id = request.POST.get('patron_id')
        item_ids = request.POST.getlist('item_ids')
        
        patron = get_object_or_404(Patron, id=patron_id)
        
        for item_id in item_ids:
            media_item = get_object_or_404(MediaItem, id=item_id)
            if media_item.status == 'available':
                due_date = timezone.now() + timedelta(days=media_item.get_loan_period_days())
                Checkout.objects.create(
                    patron=patron,
                    media_item=media_item,
                    due_date=due_date
                )
                media_item.status = 'checked_out'
                media_item.save()
                
                ActivityLog.objects.create(
                    action='checkout',
                    patron=patron,
                    media_item=media_item,
                    librarian=librarian,
                    description=f'Checked out "{media_item.title}" to {patron.name}'
                )
        
        messages.success(request, f'Successfully checked out {len(item_ids)} item(s) to {patron.name}.')
        return redirect('librarian_checkout')
    
    patrons = Patron.objects.filter(status='active')[:20]
    available_items = MediaItem.objects.filter(status='available')[:20]
    
    return render(request, 'librarian/librarian-checkout.html', {
        'librarian': librarian,
        'patrons': patrons,
        'available_items': available_items,
    })

@librarian_required
def librarian_checkin(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    
    checkin_results = []
    
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        
        try:
            media_item = MediaItem.objects.get(barcode=barcode)
            checkout = Checkout.objects.filter(media_item=media_item, returned_at__isnull=True).first()
            
            if checkout:
                checkout.returned_at = timezone.now()
                checkout.save()
                
                fine_amount = checkout.calculate_fine()
                if fine_amount > 0:
                    Fine.objects.create(
                        patron=checkout.patron,
                        checkout=checkout,
                        amount=fine_amount,
                        reason=f'Overdue fine for "{media_item.title}"'
                    )
                
                media_item.status = 'available'
                media_item.save()
                
                ActivityLog.objects.create(
                    action='checkin',
                    patron=checkout.patron,
                    media_item=media_item,
                    librarian=librarian,
                    description=f'Checked in "{media_item.title}" from {checkout.patron.name}'
                )
                
                checkin_results.append({
                    'item': media_item,
                    'patron': checkout.patron,
                    'due_date': checkout.due_date,
                    'is_overdue': checkout.is_overdue(),
                    'days_overdue': checkout.days_overdue(),
                    'fine': fine_amount,
                })
                
                messages.success(request, f'Successfully checked in "{media_item.title}"')
            else:
                messages.error(request, 'This item is not currently checked out.')
        except MediaItem.DoesNotExist:
            messages.error(request, 'Item not found.')
    
    recent_checkins = Checkout.objects.filter(returned_at__isnull=False).order_by('-returned_at')[:10]
    
    return render(request, 'librarian/librarian-checkin.html', {
        'librarian': librarian,
        'checkin_results': checkin_results,
        'recent_checkins': recent_checkins,
    })

@librarian_required
def librarian_requests(request):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    status_filter = request.GET.get('status', 'pending')
    
    requests = MediaRequest.objects.all()
    
    if status_filter and status_filter != 'all':
        requests = requests.filter(status=status_filter)
    
    pending_count = MediaRequest.objects.filter(status='pending').count()
    approved_count = MediaRequest.objects.filter(status='approved').count()
    rejected_count = MediaRequest.objects.filter(status='rejected').count()
    
    return render(request, 'librarian/librarian-requests.html', {
        'librarian': librarian,
        'requests': requests.order_by('-requested_at')[:20],
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    })

@librarian_required
def librarian_approve_request(request, request_id):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    media_request = get_object_or_404(MediaRequest, id=request_id)
    
    media_request.status = 'approved'
    media_request.reviewed_at = timezone.now()
    media_request.reviewed_by = librarian
    media_request.save()
    
    ActivityLog.objects.create(
        action='request_approved',
        patron=media_request.patron,
        librarian=librarian,
        description=f'Approved request for "{media_request.title}"'
    )
    
    messages.success(request, f'Request for "{media_request.title}" approved.')
    return redirect('librarian_requests')

@librarian_required
def librarian_reject_request(request, request_id):
    librarian = get_object_or_404(Librarian, id=request.session['librarian_id'])
    media_request = get_object_or_404(MediaRequest, id=request_id)
    
    media_request.status = 'rejected'
    media_request.reviewed_at = timezone.now()
    media_request.reviewed_by = librarian
    media_request.save()
    
    messages.success(request, f'Request for "{media_request.title}" rejected.')
    return redirect('librarian_requests')

def search_patrons_api(request):
    query = request.GET.get('q', '')
    patrons = Patron.objects.filter(
        Q(name__icontains=query) | Q(card_number__icontains=query) | Q(email__icontains=query)
    )[:10]
    
    data = [{
        'id': p.id,
        'name': p.name,
        'card_number': p.card_number,
        'checked_out': p.get_checked_out_count(),
        'fines': float(p.get_total_fines()),
    } for p in patrons]
    
    return JsonResponse(data, safe=False)

def search_items_api(request):
    query = request.GET.get('q', '')
    items = MediaItem.objects.filter(
        Q(title__icontains=query) | Q(barcode__icontains=query),
        status='available'
    )[:10]
    
    data = [{
        'id': i.id,
        'title': i.title,
        'author': i.author,
        'barcode': i.barcode,
        'media_type': i.media_type,
    } for i in items]
    
    return JsonResponse(data, safe=False)
