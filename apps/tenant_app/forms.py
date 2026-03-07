from django import forms
from .models import Member, MemberPayment


class NewMemberForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'placeholder': 'e.g. John Doe'
        })
    )
    contact = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'placeholder': 'e.g. John Doe'
        })
    )
    member_type = forms.ChoiceField(
        choices=Member._meta.get_field('member_type').choices,
        widget=forms.TextInput(attrs={
            'class': 'w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'placeholder': 'e.g. John Doe'
        })
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(attrs={
            'class': 'w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'placeholder': 'e.g. John Doe'
        })
    )