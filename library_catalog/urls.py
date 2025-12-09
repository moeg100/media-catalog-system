from django.contrib import admin
from django.urls import path
from catalog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/patron/', views.patron_signup, name='patron_signup'),
    path('signup/librarian/', views.librarian_signup, name='librarian_signup'),
    
    path('patron/', views.patron_dashboard, name='patron_dashboard'),
    path('patron/search/', views.patron_search, name='patron_search'),
    path('patron/checked-out/', views.patron_checked_out, name='patron_checked_out'),
    path('patron/renew/<int:checkout_id>/', views.patron_renew, name='patron_renew'),
    path('patron/holds/', views.patron_holds, name='patron_holds'),
    path('patron/hold/<int:item_id>/', views.patron_place_hold, name='patron_place_hold'),
    path('patron/hold/cancel/<int:hold_id>/', views.patron_cancel_hold, name='patron_cancel_hold'),
    path('patron/requests/', views.patron_requests, name='patron_requests'),
    
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('librarian/catalog/', views.librarian_catalog, name='librarian_catalog'),
    path('librarian/catalog/add/', views.librarian_add_item, name='librarian_add_item'),
    path('librarian/catalog/delete/<int:item_id>/', views.librarian_delete_item, name='librarian_delete_item'),
    path('librarian/patrons/', views.librarian_patrons, name='librarian_patrons'),
    path('librarian/checkout/', views.librarian_checkout, name='librarian_checkout'),
    path('librarian/checkin/', views.librarian_checkin, name='librarian_checkin'),
    path('librarian/requests/', views.librarian_requests, name='librarian_requests'),
    path('librarian/requests/approve/<int:request_id>/', views.librarian_approve_request, name='librarian_approve_request'),
    path('librarian/requests/reject/<int:request_id>/', views.librarian_reject_request, name='librarian_reject_request'),
    
    path('api/patrons/search/', views.search_patrons_api, name='search_patrons_api'),
    path('api/items/search/', views.search_items_api, name='search_items_api'),
]
