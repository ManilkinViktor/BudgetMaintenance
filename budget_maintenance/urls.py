from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Wallet URLs
    path('wallets/', views.WalletListView.as_view(), name='wallet_list'),
    path('wallets/add/', views.WalletCreateView.as_view(), name='wallet_create'),
    path('wallets/<int:pk>/', views.WalletUpdateView.as_view(), name='wallet_update'),
    path('wallets/<int:pk>/delete/', views.WalletDeleteView.as_view(), name='wallet_delete'),
]