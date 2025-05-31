from datetime import timedelta

from django import forms
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction, Category, Wallet
from .forms import StatsFilterForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user = self.request.user
            today = timezone.now()
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Агрегация данных
            transactions = Transaction.objects.filter(user=user, date__gte=start_of_month)

            income = transactions.filter(category__type='income').aggregate(Sum('amount'))
            expense = transactions.filter(category__type='expense').aggregate(Sum('amount'))

            total_income = income['amount__sum'] or 0
            total_expense = expense['amount__sum'] or 0

            context = {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': total_income - total_expense,
                'recent_transactions': Transaction.objects.filter(user=user).order_by('-date')[:5],
                'current_month': start_of_month.strftime('%B %Y')
            }

        return context


class SignUpView(CreateView):
    form_class = UserCreationForm  # Стандартная форма Django
    success_url = reverse_lazy('home')
    template_name = 'signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Автоматический вход после регистрации
        login(self.request, self.object)
        return response




# Transaction CRUD
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('category', 'wallet')


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    fields = ['amount', 'type', 'wallet', 'category', 'comment', 'date']  # Добавлено date
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Настройка виджета для поля даты
        form.fields['date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        # Фильтрация связанных полей
        form.fields['wallet'].queryset = Wallet.objects.filter(user=self.request.user)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    fields = ['amount', 'type', 'wallet', 'category', 'comment', 'date']  # Добавлено date
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        form.fields['wallet'].queryset = Wallet.objects.filter(user=self.request.user)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# Category CRUD
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['title', 'type']
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['title', 'type']
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


# Wallet CRUD
class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'wallet_list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    fields = ['title', 'amount', 'proportion', 'description']
    template_name = 'wallet_form.html'
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Wallet
    fields = ['title', 'amount', 'proportion', 'description']
    template_name = 'wallet_form.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class WalletDeleteView(LoginRequiredMixin, DeleteView):
    model = Wallet
    template_name = 'wallet_confirm_delete.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)





class StatsView(TemplateView):
    template_name = 'stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = StatsFilterForm(self.request.user, self.request.GET or None)

        if form.is_valid():
            wallet_id = form.cleaned_data['wallet']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            wallet_id = 'all'
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

        # Фильтрация транзакций
        transactions = Transaction.objects.filter(
            user=self.request.user,
            date__date__range=[start_date, end_date]
        )

        if wallet_id != 'all':
            transactions = transactions.filter(wallet_id=wallet_id)

        # Статистика
        total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expence = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        if total_income:
            income_by_category = transactions.filter(type='income').values('category__title').annotate(
                total=Sum('amount'), part=100 * Sum('amount') / total_income)
        else:
            income_by_category = transactions.filter(type='income').values('category__title').annotate(total=Sum('amount'))

        if total_expence:
            expense_by_category = transactions.filter(type='expense').values('category__title').annotate(
                total=Sum('amount'), part=100 * Sum('amount') / total_expence if total_expence else 0)
        else:
            expense_by_category = transactions.filter(type='expense').values('category__title').annotate(total=Sum('amount'))


        context.update({
            'form': form,
            'start_date': start_date,
            'end_date': end_date,
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category,
            'total_income': total_income,
            'total_expense': total_expence,
            'balance': total_income - total_expence,
        })
        return context