from django.urls import path
from myapp import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/",views.register,name="register"),
    path('preregister/', views.preregister, name="preregister"),
    path('login/', views.login, name="login"),
    path('login-form/', views.login_form, name="login-form"),
    path('user/login-form/<int:user_id>/', views.login_form_for_seller_profile, name="login-form-seller"),
    path('logout/', views.logout, name="logout"),
    path("products_list/",views.products_list,name="products_list"),
    path('add-product/', views.add_product, name='add_product'),
    path('search/', views.product_search, name='product_search'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('profile/', views.user_profile, name='user_profile'),
    path('change_profile_picture/', views.change_profile_picture, name='change_profile_picture'),
    path('user/<int:user_id>/', views.seller_profile, name='seller_profile'),
    path('products/', views.filtered_products,name='filtered_products'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('buy/<int:product_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),#mozda obrisat
    path('transaction/<int:transaction_id>',views.transaction_detail, name='transaction_detail'),
    path('transaction/<int:transaction_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('product/<int:product_id>/payment_success/', views.payment_success, name='payment_success'),
]

