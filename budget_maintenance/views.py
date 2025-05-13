from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Transaction
from django.db.models import Sum
from django.utils import timezone


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
