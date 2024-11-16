from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .forms import ProfileForm, ProductForm, ProfilePictureForm
from .models import Product,Profile, Transaction, Notification
from django.http import JsonResponse
from decimal import Decimal
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from myapp.management.commands.proba import Command as RecommendCommand
from django.template.loader import render_to_string
from weasyprint import HTML
from django.urls import reverse

def home(request):
    return render(request,'advertisement/home.html')

def product_search(request):
    query = request.GET.get('searched', '')
    selected_categories = request.GET.getlist('category', [])
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 10000)

    products = Product.objects.filter(status="Dostupno")

    if query:
        products = products.filter(title__icontains=query)
    
    if selected_categories:
        products = products.filter(category__in=selected_categories)
    
    products = products.filter(price__gte=min_price, price__lte=max_price)
    
    categories = [choice[0] for choice in Product.CATEGORY_CHOICES]

    context = {
        'products': products,
        'search_query': query,
        'categories': categories,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'advertisement/products_list.html', context)

def products_list(request):
    selected_categories = request.GET.getlist('category')

    products = Product.objects.filter(status="Dostupno")

    if selected_categories:
        products = products.filter(category__in=selected_categories)

    categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': selected_categories,
    }

    return render(request, 'advertisement/products_list.html', context)

def filtered_products(request):
    selected_categories = request.GET.getlist('category', Product.CATEGORY_CHOICES)

    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 10000)

    products = Product.objects.filter(
        status="Dostupno",
        category__in=selected_categories,
        price__gte=min_price,
        price__lte=max_price
    )

    categories = [choice[0] for choice in Product.CATEGORY_CHOICES]

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'advertisement/products_list.html', context)

def preregister(request):
    return render(request, "registration/preregister.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        name = request.POST['name']
        surname = request.POST['surname']
        city = request.POST['city']
        address = request.POST['address']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Korisničko ime je već iskorišteno!')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Lozinke se ne podudaraju!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email adresa je već iskorištena!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.name = name
            profile.surname = surname
            profile.city = city
            profile.address = address
            profile.save()
            messages.success(request, 'Registracija uspješna! Možete se prijaviti.')
            return redirect('login')

    else:
        form = ProfileForm()
        
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect(reverse('home'))
        else:
            messages.info(request,"Netočna lozinka!")
            return redirect('login')
    else:
        return render(request,'registration/login.html')
    
def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect(reverse('login-form'))
        else:
            messages.info(request,"Netočna lozinka!")
            return redirect('login-form')
    else:
        return render(request,'advertisement/home.html')

def login_form_for_seller_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    products = user.product_set.filter(status="Dostupno")

    context = {
        'profile': profile,
        'products': products,
        'user_id': user_id  
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        authenticated_user = auth.authenticate(username=username, password=password)

        if authenticated_user is not None:
            auth.login(request, authenticated_user)
            return render(request, 'accounts/seller_profile.html', context)
        else:
            messages.info(request, "Netočna lozinka!")
            return render(request, 'accounts/seller_profile.html', context)

    return render(request, 'accounts/seller_profile.html', context)
    
@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect(reverse('product_detail', args=[product.id])) 
    else:
        form = ProductForm()
    return render(request, 'advertisement/add_product.html', {'form': form})

def product_detail(request, product_id):
    item = get_object_or_404(Product, id=product_id)
    
    conversion_rate = Decimal('7.5')
    kn_price = item.price * conversion_rate
    
    recommender = RecommendCommand()
    similar_products = recommender.recommend_similar_products(product_id) 
    
    recommended_product_ids = [product['id'] for product in similar_products]
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)[:3]

    session_id = request.GET.get('session_id') 

    context = {
        'item': item,
        'kn_price': kn_price,
        'recommended_products': recommended_products,
        'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
        'session_id': session_id 
    }
    
    return render(request, 'advertisement/detail.html', context)

@login_required
def user_profile(request):
    profile = request.user.profile 
    products = Product.objects.filter(seller=request.user)  
    
    context = {
        'profile': profile,
        'products': products
    }

    return render(request, 'accounts/user_profile.html', context)

@login_required
def change_profile_picture(request):
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  
        else:
            return render(request, 'accounts/user_profile.html', {
                'profile': profile,
                'form': form,
                'form_errors': form.errors
            })
    else:
        form = ProfilePictureForm(instance=profile)
    
    return render(request, 'accounts/user_profile.html', {
        'profile': profile,
        'form': form
    })


def seller_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    products = user.product_set.filter(status="Dostupno")

    context = {
        'profile': profile,
        'products': products,
        'user_id': user_id  
    }
    
    return render(request, 'accounts/seller_profile.html', context)

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'advertisement/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user != product.seller:
        return redirect('products_list')  
    
    if request.method == 'POST':
        product.delete()
        return redirect('user_profile')  

    return redirect('products_list')  

stripe.api_key = settings.STRIPE_SECRET_KEY



def create_checkout_session(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.title,
                    },
                    'unit_amount': int(product.price * 100),  
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success', args=[product_id]) + '?payment_success=true'), 
            cancel_url=request.build_absolute_uri(reverse('payment_success', args=[product_id]) + '?payment_success=false&cancel=true'),
            metadata={
                'product_id': product_id,
                'buyer_id': request.user.id,  
            }
        )

        print(f"Stripe session created: {session.id}")  
        return JsonResponse({'id': session.id})

    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if transaction.buyer == request.user or transaction.seller == request.user:
        notifications = Notification.objects.filter(transaction=transaction, receiver=request.user, is_read=False)

        for notification in notifications:
            notification.is_read = True
            notification.save()

    context = {
        'transaction': transaction
    }
    return render(request, 'advertisement/transaction_detail.html', context)

def generate_invoice(request, transaction_id):

    transaction = get_object_or_404(Transaction, id=transaction_id)

    html_string = render_to_string('advertisement/transaction.html', {'transaction': transaction})

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="račun_{transaction.id}.pdf"'

    return response

def payment_success(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    buyer = request.user
    seller = product.seller
    item = get_object_or_404(Product, id=product_id)
    conversion_rate = Decimal('7.5')
    kn_price = item.price * conversion_rate
    
    recommender = RecommendCommand()
    similar_products = recommender.recommend_similar_products(product_id) 
    
    recommended_product_ids = [product['id'] for product in similar_products]
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)[:3]

    session_id = request.GET.get('session_id') 
    if request.GET.get('payment_success') == 'true':

        transaction = Transaction.objects.create(
            product=product,
            buyer=buyer,
            seller=seller,
            amount=product.price,
            status='C',  
            stripe_payment_id='dummy_payment_id' 
        )

        Notification.objects.create(
            receiver=buyer,
            sender=seller,
            message=f"Uspješno ste kupili proizvod: {product.title}.",
            is_read=False,
            transaction=transaction,
            type=2
        )

        Notification.objects.create(
            receiver=seller,
            sender=buyer,
            message=f"Vaš proizvod '{product.title}' je uspješno prodan.",
            is_read=False,
            transaction=transaction,
            type=2
        )
        print(f"Transaction and notifications created for buyer {buyer.id} and seller {seller.id}")

        item.quantity  = product.quantity-1

        if item.quantity == 0:
            item.status = "Nedostupno"
        item.save()
    context = {
        'item': item,
        'kn_price': kn_price,
        'recommended_products': recommended_products,
        'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
        'session_id': session_id 
        }
    return render(request, 'advertisement/detail.html', context) 







### OBRISAT PO POTREBI ##
@csrf_exempt
def stripe_webhook(request):
    print("Webhook received")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print("Webhook verified")  
    except ValueError:
        print("Invalid payload.")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        print("Invalid signature.")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Session data:", session)  

        product_id = session["metadata"].get("product_id")
        buyer_id = session["metadata"].get("buyer_id")

        try:
            product = Product.objects.get(id=product_id)
            buyer = User.objects.get(id=buyer_id)
            seller = product.seller
            transaction = Transaction.objects.create(
                product = product,
                buyer = buyer,
                seller = seller,
                amount = product.price,
                status = 'C',
                stripe_payment_id = session.id
            )
            Notification.objects.create(
                receiver=buyer,
                sender=seller,
                message=f"Uspješno ste kupili proizvod: {product.title}.",
                is_read=False,
                transaction = transaction,
                type = 2
            )

            Notification.objects.create(
                receiver=seller,
                sender=buyer,
                message=f"Vaš proizvod '{product.title}' je uspješno prodan.",
                is_read=False,
                transaction = transaction,
                type = 2
            )

            print(f"Notifications created for buyer {buyer.id} and seller {seller.id}")

        except Product.DoesNotExist:
            print(f"Product with ID {product_id} does not exist.")
            return HttpResponse(status=404)
        except User.DoesNotExist:
            print(f"User with ID {buyer_id} does not exist.")
            return HttpResponse(status=404)
        except Exception as e:
            print(f"Error handling notification creation: {e}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)