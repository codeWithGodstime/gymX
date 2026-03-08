from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView
from allauth.account.views import LoginView, LogoutView
from django.utils.text import slugify
from django.db.transaction import atomic
from allauth.account.utils import perform_login

from apps.public_app.models import Gym, Domain, SubscriptionPlan
from apps.public_app.paystack import PaystackSubscriptionManager
from .forms import GymOwnerForm, UserSignupForm
from formtools.wizard.views import SessionWizardView

from apps.public_app.models import Subscription

User = get_user_model()


class GymOwnerSignupWizard(SessionWizardView):
    form_list = [("user", UserSignupForm), ("gym", GymOwnerForm)]
    templates = {  # Correct spelling
        "user": "account/signup.html",
        "gym": "account/signup_gym.html"
    }

    def get_template_names(self):
        return [self.templates.get(self.steps.current, self.template_name)]

    @atomic
    def done(self, form_list, **kwargs):
        form_data = self.get_all_cleaned_data()
        print(f"[WIZARD] Form data collected: {form_data}")

            # Safe schema name
        schema_name = slugify(form_data["gym_name"]).replace("-", "")
        print(f"[WIZARD] Generated schema name: {schema_name}")
        
        # clean domain name
        domain = settings.DOMAIN_HOST.replace("http://", "").replace("https://", "").split(":")[0]  # Remove protocol and port
        # Create Gym tenant
        schema_name = form_data['custom_subdomain'].lower().replace(" ", "")
        tenant = Gym.objects.create(
            schema_name=schema_name,
            name=form_data['gym_name']
        )
        print(f"[WIZARD] Gym created - ID: {tenant.id}, Name: {tenant.name}, Schema: {tenant.schema_name}")

        # Create Domain
        domain = Domain.objects.create(
            domain=f"{schema_name}.{domain}",
            tenant=tenant,
            is_primary=True
        )
        print(f"[WIZARD] Domain created: {domain.domain}")

        # Create User
        user = User.objects.create_user(
            email=form_data['email'],
            password=form_data['password1'],
            username=schema_name,
            tenant=tenant
        )
        print(f"[WIZARD] User created - ID: {user.id}, Email: {user.email}")

        user.is_active = True
        user.save()
        
        # create free trial subscription
        Subscription.objects.create(
            tenant=tenant,
            plan=None,
            status="active",
        )

        from allauth.account.utils import perform_login
        perform_login(self.request, user, email_verification='optional')

        scheme = "http" if settings.DEBUG else "https"
        port = ":8000" if settings.DEBUG else ""
        redirect_url = f"{scheme}://{domain.domain}{port}/accounts/overview/"
        return redirect(redirect_url)


class TenantLoginView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = False

    def form_valid(self, form):
        # This calls the allauth login logic → sets session, logs user in
        response = super().form_valid(form)

        # Now request.user should be the real user (not AnonymousUser)
        user = self.request.user

        if user.is_authenticated and hasattr(user, 'tenant') and user.tenant:
            tenant = user.tenant
            tenant_domain = tenant.domains.filter(is_primary=True).first()

            if tenant_domain:
                scheme = "http" if settings.DEBUG else "https"
                port = ":8000" if settings.DEBUG else ""
                # Use the path the user was trying to reach, or fallback to dashboard
                next_path = self.request.GET.get('next') or '/accounts/overview/'
                redirect_url = f"{scheme}://{tenant_domain.domain}{port}{next_path}"
                return redirect(redirect_url)
            
        return response


class TenantLogoutView(LogoutView):
    template_name = 'account/logout.html'

    def get_next_page(self):
        next_page = super().get_next_page()
        if next_page:
            return next_page
        return reverse('accounts:login')


class SubscriptionView(TemplateView):
    template_name = 'account/subscription.html'
    
    def get(self, request, *args, **kwargs):
        # Check if user has signed up (session data exists)
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all subscription plans from database
        plans = SubscriptionPlan.objects.all().order_by('amount')
        
        print(f"[VIEW] SubscriptionView - Retrieved {plans.count()} plans")
        for plan in plans:
            print(f"[VIEW] SubscriptionView - Plan: {plan.name}, Amount: {plan.amount}, Code: {plan.paystack_plan_code}")
        
        context['plans'] = plans
        
        return context


class InitializePaymentView(TemplateView):
    """Initialize Paystack payment - handles POST from subscription page and redirects to Paystack"""
    
    def post(self, request, *args, **kwargs):
        # Handle payment processing with Paystack
        plan = request.POST.get('plan')
        
        print(f"[VIEW] InitializePaymentView - Selected plan: {plan}")
        
        # Validate plan
        if not plan:
            messages.error(request, 'Please select a plan.')
            return redirect('subscription')
        
        # Get user and tenant from session
        if 'new_user_id' not in request.session or 'new_tenant_id' not in request.session:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect('account_signup')
        
        try:
            user = User.objects.get(id=request.session['new_user_id'])
            tenant = Gym.objects.get(id=request.session['new_tenant_id'])
            
            print(f"[VIEW] InitializePaymentView - User: {user.email}, Tenant: {tenant.name}")
            
            # Get subscription plan
            sub_plan = SubscriptionPlan.objects.get(name=plan)
            
            print(f"[VIEW] InitializePaymentView - Plan details - Name: {sub_plan.name}, Amount: {sub_plan.amount}, Code: {sub_plan.paystack_plan_code}")
            
            # Check if plan has Paystack plan code
            if not sub_plan.paystack_plan_code:
                messages.error(request, 'Payment plan not configured properly.')
                print(f"[VIEW] InitializePaymentView - ERROR: Plan code not configured")
                return redirect('subscription')
            
            # Initialize Paystack transaction
            paystack_manager = PaystackSubscriptionManager()
            email = request.session.get('signup_data', {}).get('email', user.email)
            
            # Create callback URL
            callback_url = request.build_absolute_uri('/accounts/payment/callback/')
            
            print(f"[VIEW] InitializePaymentView - Email: {email}, Callback URL: {callback_url}")
            
            transaction_response = paystack_manager.initialize_subscription_transaction(
                email=email,
                plan_code=sub_plan.paystack_plan_code,
                callback_url=callback_url
            )
            
            print(f"[VIEW] InitializePaymentView - Transaction response status: {transaction_response.get('status')}")
            
            if transaction_response.get('status'):
                # Store transaction reference in session for callback
                request.session['paystack_reference'] = transaction_response['data']['reference']
                request.session['payment_plan'] = plan
                
                print(f"[VIEW] InitializePaymentView - Redirecting to Paystack - Reference: {transaction_response['data']['reference']}")
                
                # Redirect to Paystack payment page
                return redirect(transaction_response['data']['authorization_url'])
            else:
                messages.error(request, 'Failed to initialize payment. Please try again.')
                print(f"[VIEW] InitializePaymentView - ERROR: Payment initialization failed - {transaction_response}")
                return redirect('subscription')
        
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid plan selected.')
            print(f"[VIEW] InitializePaymentView - ERROR: Plan not found - {plan}")
            return redirect('subscription')
        except Exception as e:
            messages.error(request, f'Payment initialization failed: {str(e)}')
            print(f"[VIEW] InitializePaymentView - EXCEPTION: {str(e)}")
            return redirect('subscription')


class PaymentCallbackView(TemplateView):
    """Handle Paystack callback after payment"""
    
    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        
        print(f"[VIEW] PaymentCallbackView - Callback received with reference: {reference}")
        
        if not reference:
            messages.error(request, 'Invalid payment reference.')
            print(f"[VIEW] PaymentCallbackView - ERROR: No reference provided")
            return redirect('account_signup')
        
        # Get data from session
        if 'new_user_id' not in request.session or 'new_tenant_id' not in request.session:
            messages.error(request, 'Session expired. Please sign up again.')
            print(f"[VIEW] PaymentCallbackView - ERROR: Session data missing")
            return redirect('account_signup')
        
        try:
            user = User.objects.get(id=request.session['new_user_id'])
            tenant = Gym.objects.get(id=request.session['new_tenant_id'])
            
            print(f"[VIEW] PaymentCallbackView - User: {user.email}, Tenant: {tenant.name}")
            
            # Verify payment with Paystack
            paystack_manager = PaystackSubscriptionManager()
            subscription = paystack_manager.handle_payment_success(reference, tenant)
            
            print(f"[VIEW] PaymentCallbackView - Payment handler result: {subscription}")
            
            if subscription:
                # Clean up session
                session_keys = ['signup_data', 'new_user_id', 'new_tenant_id', 'paystack_reference', 'payment_plan']
                for key in session_keys:
                    if key in request.session:
                        del request.session[key]
                
                # Redirect to tenant dashboard
                tenant_domain = f"{tenant.schema_name}.{settings.DOMAIN_HOST}"
                print(f"[VIEW] PaymentCallbackView - SUCCESS: Subscription created, redirecting to {tenant_domain}")
                messages.success(request, f'Welcome to GymX! Your {subscription.plan.name} plan is now active.')
                return redirect(f"http://{tenant_domain}/accounts/dashboard/")
            else:
                messages.error(request, 'Payment verification failed. Please contact support.')
                print(f"[VIEW] PaymentCallbackView - ERROR: Payment handler returned False")
                return redirect('account_signup')
                
        except Exception as e:
            messages.error(request, f'Payment processing failed: {str(e)}')
            print(f"[VIEW] PaymentCallbackView - EXCEPTION: {str(e)}")
            return redirect('account_signup')