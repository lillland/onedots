from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import UserCreationForm
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from designweb.serializer import *
from designweb.forms import *
from designweb.utils import *
from django.http import HttpResponse
import json


def home(request):
    return render(request, 'home.html', get_display_dict(title='HOME'))


def index(request):
    print(request.session)
    return render(request, 'index.html', {'title': 'HOME', })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            user = authenticate(username=username, password=password)
            # create one to one rel instances for new user
            user.user_profile = UserProfile.objects.create(user=user)
            user.user_profile.first_name = first_name
            user.user_profile.last_name = last_name
            user.user_profile.save()
            user.cart = Cart.objects.create(user=user)
            user.wish_list = WishList.objects.create(user=user)
            sending_mail_for_new_signup(username)
            login(request, user)
            return render(request, 'home.html', get_display_dict(title='HOME', pass_dict={'welcome': True, }))
        else:
            pass_dicts = {'form': form, 'error_msg': form.error_messages}
            return render(request, 'signup.html', get_display_dict('SIGNUP', pass_dict=pass_dicts))
    else:
        form = UserCreationForm()
        return render(request, 'signup.html', get_display_dict('SIGNUP', pass_dict={'form': form, }))


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('design:home'), get_display_dict(title='HOME'))
        else:
            return render(request, 'login.html', get_display_dict(title='LOGIN'))
    else:
        return render(request, 'login.html', get_display_dict(title='LOGIN'))


def logout_view(request):
    logout(request)
    return redirect(reverse('design:home'))


# first show up for new register customer
@login_required(login_url='/login/')
@api_view(['GET', 'POST', ])
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user is not None:
            user.user_profile.gender = request.POST['gender']
            user.user_profile.designer_type = request.POST['designer_type']
            user.user_profile.address1 = request.POST['address1']
            user.user_profile.address2 = request.POST['address2']
            user.user_profile.city = request.POST['city']
            user.user_profile.state = request.POST['state']
            user.user_profile.zip = request.POST['zip']
            user.user_profile.save()
            return redirect(reverse('design:home'), get_display_dict('HOME'))

    pass_dicts = {'designer_type': user.user_profile.designer_type,
                  'gender': user.user_profile.gender,
                  'address1': user.user_profile.address1,
                  'address2': user.user_profile.address2,
                  'city': user.user_profile.city,
                  'state': user.user_profile.state,
                  'zip': user.user_profile.zip, }
    return render(request, 'user_profile.html', get_display_dict('USER PROFILE', pass_dict=pass_dicts))


@ensure_csrf_cookie
def product_view(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    show_create = False
    micro_group = is_user_already_in_group(user, product)
    if micro_group is None:
        show_create = True
    pass_dicts = {'product': product,
                  'show_create': show_create,
                  'group': micro_group,
                  'is_in_cart': is_product_in_user_cart(user, pk)}
    return render(request, 'product.html', (get_display_dict('PRODUCT', pass_dict=pass_dicts)))


"""     --Ajax views--      """
@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
def add_cart(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    user.cart.products.add(product)
    if not is_product_in_cart_details(user, product):
        user.cart.cart_details.create(cart=user.cart, product=product)
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
def add_wish(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    user.wish_list.products.add(product)
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
def remove_cart(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    user.cart.products.remove(product)
    if is_product_in_cart_details(user, product):
        user.cart.cart_details.filter(product=product).delete()
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
def remove_wish(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    user.wish_list.products.remove(product)
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
@login_required(login_url='/login/')
def update_order_detail(request, pk, num):
    order_detail = get_object_or_404(OrderDetails, pk=pk)
    order_detail.number_items = num
    order_detail.save()
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
@login_required(login_url='/login/')
def update_cart_detail(request, pk, num):
    cart_detail = get_object_or_404(CartDetail, pk=pk)
    cart_detail.number_in_cart = num
    cart_detail.save()
    return Response(data={'Success': 'Success'})


@ensure_csrf_cookie
@api_view(['GET', 'POST', ])
def like_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.number_like += 1
    product.save()
    return Response(data={'Success': 'Success'})


# ===============================================
@ensure_csrf_cookie
@login_required(login_url='/login/')
def my_cart(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user is not None:
        products = user.cart.products.all()
        pass_dicts = {'products': products, 'orders': user.cart.cart_details.all()}
        return render(request, 'mycart.html', get_display_dict('MY CART', pass_dict=pass_dicts))


@ensure_csrf_cookie
@login_required(login_url='/login/')
def my_wish(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user is not None:
        products = user.wish_list.products.all()
        pass_dicts = {'products': products, }
        return render(request, 'mywishlist.html', get_display_dict('MY WISH LIST', pass_dict=pass_dicts))
# ===============================================


@ensure_csrf_cookie
@login_required(login_url='/login/')
def my_order(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_authenticated():
        details = user.cart.cart_details.all()
        products = []
        for detail in details:
            products.append(detail.product)
        order = user.orders.get_or_create(user=user, is_paid=False)[0]
        for item in details:
            if not is_order_list_contain_product(order.details.all(), item.product.pk):
                OrderDetails.objects.create(order=order, product=item.product, number_items=item.number_in_cart)
            else:
                order_detail = OrderDetails.objects.get(order=order, product=item.product)
                order_detail.number_items = item.number_in_cart
                order_detail.save()
        for item in order.details.all():
            if not is_cart_list_contain_order_detail(products, item.product.pk):
                order.details.filter(pk=item.pk).delete()
        pass_dicts = {'orders': order.details, 'order_id': order.pk, }
        profile = get_profile_address_or_empty(user)
        if profile:
            pass_dicts['profile'] = profile
        return render(request, 'myorder.html', get_display_dict('MY ORDER', pass_dict=pass_dicts))


def category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    pass_dicts = {'products': products, }
    return render(request, 'category.html', get_display_dict('CATEGORY', pass_dict=pass_dicts))


def micro_group_view(request, product_id, group_id=None):
    product = get_object_or_404(Product, pk=product_id)
    show_join = False
    user = request.user

    if product is None:
        return

    if group_id is None or not isinstance(group_id, int):   # inside call
        if user.is_authenticated():
            micro_group = is_user_already_in_group(user, product)
            if micro_group is None:
                # create new group for this user
                group_price = product.price * product.group_discount
                micro_group = MicroGroup.objects.create(product=product, owner=user, is_active=True,
                                                        group_price=group_price, group_discount=product.group_discount)
                micro_group.members.add(user)
            total_members = micro_group.members.count()
            pass_dicts = {'group': micro_group,
                          'product': micro_group.product,
                          'show_join': show_join,
                          'remain_time': micro_group.get_remain_time_by_seconds(),
                          'total_members': total_members, }
            return render(request, 'microgroup.html', get_display_dict('M-GROUP', pass_dict=pass_dicts))
        else:
            return redirect(reverse('design:login'), get_display_dict('LOGIN'))
    else:   # outside call
        group = get_object_or_404(MicroGroup, pk=group_id)
        if group is not None:
            total_members = group.members.count()
            if not group.objects.filter(user=user).exists():
                show_join = True
            pass_dicts = {'group': group,
                          'product': group.product[0],
                          'show_join': show_join,
                          'remain_time': group.get_remain_time_by_seconds(),
                          'total_members': total_members, }
            return render(request, 'microgroup.html', get_display_dict('M-GROUP', pass_dict=pass_dicts))
        else:
            return redirect(reverse('design:home', get_display_dict('HOME')))


@ensure_csrf_cookie
@login_required(login_url='/login/')
def update_order_info(request, pk, order_id):
    shipping_data = {
        'shipping_address1': request.POST.get('shipping_address1'),
        'shipping_address2': request.POST.get('shipping_address2'),
        'shipping_city': request.POST.get('shipping_city'),
        'shipping_state': request.POST.get('shipping_state'),
        'shipping_zip': request.POST.get('shipping_zip'),
        'shipping_phone1': request.POST.get('shipping_phone1'),
        'shipping_phone2': request.POST.get('shipping_phone2'),
        'billing_address1': request.POST.get('billing_address1'),
        'billing_address2': request.POST.get('billing_address2'),
        'billing_city': request.POST.get('billing_city'),
        'billing_state': request.POST.get('billing_state'),
        'billing_zip': request.POST.get('billing_zip'),
        'billing_phone1': request.POST.get('billing_phone1'),
        'billing_phone2': request.POST.get('billing_phone2'),
    }

    msg = update_order_address_info(pk, order_id, shipping_data)
    response_data = {}
    try:
        response_data['result'] = 'writing successful !'
    except:
        response_data['message'] = 'failed processing ...\n' + msg
    return HttpResponse(json.dumps(response_data), content_type='application/json')


# ===============================================
class ProductsList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class WishListViewSet(viewsets.ModelViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
# ===============================================