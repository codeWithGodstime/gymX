import requests
import json
from django.conf import settings
from .models import Subscription, Gym, SubscriptionPlan


class PaystackAPI:
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_transaction(self, email, plan_code, amount=None, callback_url=None):
        """
        Initialize a transaction with a plan code for subscription
        """
        url = f"{self.BASE_URL}/transaction/initialize"
        
        data = {
            'email': email,
            'plan': plan_code,
            "amount": amount
        }
        
        if amount:
            data['amount'] = amount
        if callback_url:
            data['callback_url'] = callback_url
            
        print(f"[PAYSTACK] Initializing transaction - URL: {url}")
        print(f"[PAYSTACK] Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=self.headers, json=data)
        
        print(f"[PAYSTACK] Response status code: {response.status_code}")
        print(f"[PAYSTACK] Response data: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    
    def verify_transaction(self, reference):
        """
        Verify a transaction status
        """
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        
        print(f"[PAYSTACK] Verifying transaction - URL: {url}")
        print(f"[PAYSTACK] Reference: {reference}")
        
        response = requests.get(url, headers=self.headers)
        
        print(f"[PAYSTACK] Response status code: {response.status_code}")
        print(f"[PAYSTACK] Response data: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    
    def create_subscription(self, customer_code, plan_code, authorization_code=None):
        """
        Create a subscription directly (alternative to plan code in transaction)
        """
        url = f"{self.BASE_URL}/subscription"
        
        data = {
            'customer': customer_code,
            'plan': plan_code
        }
        
        if authorization_code:
            data['authorization'] = authorization_code
            
        print(f"[PAYSTACK] Creating subscription - URL: {url}")
        print(f"[PAYSTACK] Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=self.headers, json=data)
        
        print(f"[PAYSTACK] Response status code: {response.status_code}")
        print(f"[PAYSTACK] Response data: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    
    def fetch_subscription(self, subscription_code):
        """
        Fetch subscription details
        """
        url = f"{self.BASE_URL}/subscription/{subscription_code}"
        
        print(f"[PAYSTACK] Fetching subscription - URL: {url}")
        print(f"[PAYSTACK] Subscription code: {subscription_code}")
        
        response = requests.get(url, headers=self.headers)
        
        print(f"[PAYSTACK] Response status code: {response.status_code}")
        print(f"[PAYSTACK] Response data: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    
    def cancel_subscription(self, subscription_code, token=None):
        """
        Cancel a subscription
        """
        url = f"{self.BASE_URL}/subscription/{subscription_code}"
        data = {}
        if token:
            data['token'] = token
            
        print(f"[PAYSTACK] Canceling subscription - URL: {url}")
        print(f"[PAYSTACK] Request data: {json.dumps(data, indent=2)}")
        
        response = requests.delete(url, headers=self.headers, json=data)
        
        print(f"[PAYSTACK] Response status code: {response.status_code}")
        print(f"[PAYSTACK] Response data: {json.dumps(response.json(), indent=2)}")
        
        return response.json()


class PaystackSubscriptionManager:
    def __init__(self):
        self.api = PaystackAPI()
    
    def initialize_subscription_transaction(self, email, plan_code, callback_url=None):
        """
        Initialize a transaction for subscription using plan code
        """
        return self.api.initialize_transaction(email, plan_code, callback_url=callback_url)
    
    def handle_payment_success(self, reference, tenant):
        """
        Handle successful payment and create subscription record
        Called when payment is verified as successful
        """
        print(f"[PAYMENT_HANDLER] Processing payment - Reference: {reference}, Tenant: {tenant.id}")
        
        # Verify the transaction
        verification = self.api.verify_transaction(reference)
        
        print(f"[PAYMENT_HANDLER] Verification result: {verification.get('status')}")
        
        if verification.get('status') and verification['data']['status'] == 'success':
            data = verification['data']
            
            print(f"[PAYMENT_HANDLER] Payment successful - Processing subscription")
            print(f"[PAYMENT_HANDLER] Transaction data: {json.dumps(data, indent=2, default=str)}")
            
            # Get the plan from the transaction data
            plan_code = data.get('plan_object', {}).get('plan_code')
            print(f"[PAYMENT_HANDLER] Plan code from response: {plan_code}")
            
            if not plan_code:
                # Fallback: get plan from metadata or other means
                # For now, assume we can get it from the subscription created
                print(f"[PAYMENT_HANDLER] Warning: No plan code found in response")
                pass
            
            # Find the subscription plan in our database
            try:
                sub_plan = SubscriptionPlan.objects.get(paystack_plan_code=plan_code)
                print(f"[PAYMENT_HANDLER] Found subscription plan: {sub_plan.name} (ID: {sub_plan.id})")
            except SubscriptionPlan.DoesNotExist:
                # Handle case where plan doesn't exist
                print(f"[PAYMENT_HANDLER] ERROR: Subscription plan not found for code: {plan_code}")
                return False
            
            # Create subscription record
            subscription = Subscription.objects.create(
                tenant=tenant,
                plan=sub_plan,
                status='active',
                paystack_subscription_code=data.get('subscription_code', ''),
            )
            
            print(f"[PAYMENT_HANDLER] Subscription created - ID: {subscription.id}, Code: {data.get('subscription_code', '')}")
            
            # Update tenant with plan and activate
            tenant.plan = sub_plan
            tenant.active = True
            tenant.save()
            
            print(f"[PAYMENT_HANDLER] Tenant updated - Tenant ID: {tenant.id}, Plan: {sub_plan.name}")
            
            return subscription
        else:
            print(f"[PAYMENT_HANDLER] Payment verification failed or status is not success")
            print(f"[PAYMENT_HANDLER] Verification data: {verification}")
        
        return False