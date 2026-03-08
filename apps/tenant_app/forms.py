from django import forms
from .models import Member, MemberPayment


class NewMemberForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(attrs={
            "class": "w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm",
            "placeholder": "e.g. 5000"
        })
    )

    class Meta:
        model = Member
        fields = ["name", "contact", "member_type"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm",
                "placeholder": "e.g. John Doe"
            }),
            "contact": forms.TextInput(attrs={
                "class": "w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm",
                "placeholder": "e.g. 08012345678"
            }),
            "member_type": forms.Select(attrs={
                "class": "w-full h-11 px-4 rounded-lg border border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-sm"
            }),
        }