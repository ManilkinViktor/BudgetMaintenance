from django import forms
from django.utils import timezone
from datetime import timedelta


class StatsFilterForm(forms.Form):
    wallet = forms.ChoiceField(
        label='Счет',
        required=False,
        choices=[]  # Будет заполнено в __init__
    )

    start_date = forms.DateField(
        label='Дата начала',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    end_date = forms.DateField(
        label='Дата окончания',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически заполняем выбор счета
        wallets = user.wallets.all()
        self.fields['wallet'].choices = [('all', 'Все счета')] + [(w.id, w.title) for w in wallets]

        # Устанавливаем значения по умолчанию (последние 30 дней)
        if not self.data:
            self.initial['end_date'] = timezone.now().date()
            self.initial['start_date'] = self.initial['end_date'] - timedelta(days=30)