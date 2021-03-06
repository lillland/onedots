from django.conf.urls import url, patterns, include
from designweb import views
from rest_framework import routers

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^user-profile/(?P<pk>[0-9]+)/$', views.user_profile, name='user-profile'),
    url(r'^product/(?P<pk>[0-9]+)/$', views.product_view, name='product-view'),
    url(r'^cart/(?P<pk>[0-9]+)/', views.my_cart, name='my-cart'),
    url(r'^wish/(?P<pk>[0-9]+)/', views.my_wish, name='my-wish'),
    url(r'^order/(?P<pk>[0-9]+)/', views.my_order, name='my-order'),
    url(r'^category/(?P<pk>[0-9]+)/', views.category_view, name='category-view'),
    # url(r'^microgroup/(?P<pk>[0-9]+)/(?P<product_id>[0-9]+)/$', views.micro_group_view, name='micro-group'),
    url(r'^microgroup/(?P<product_id>[0-9]+)/(?P<group_id>[0-9]+)/$', views.micro_group_view, name='micro-group-id'),
    url(r'^microgroup/(?P<product_id>[0-9]+)//$', views.micro_group_view, name='micro-group'),

    # api for ajax add and delete
    url(r'^api/cart/(?P<pk>[0-9]+)/add/$', views.add_cart, name='add-to-cart'),
    url(r'^api/wish/(?P<pk>[0-9]+)/add/$', views.add_wish, name='add-to-wish'),
    url(r'^api/cart/(?P<pk>[0-9]+)/remove/$', views.remove_cart, name='remove-from-cart'),
    url(r'^api/wish/(?P<pk>[0-9]+)/remove/$', views.remove_wish, name='remove-from-wish'),
    url(r'^api/order-detail/(?P<pk>[0-9]+)/(?P<num>[0-9]+)/update/$', views.update_order_detail, name='update-order'),
    url(r'^api/cart-detail/(?P<pk>[0-9]+)/(?P<num>[0-9]+)/update/$', views.update_cart_detail, name='update-cart'),
    url(r'^api/like/(?P<pk>[0-9]+)/$', views.like_product, name='like-product'),
    url(r'^api/address/(?P<pk>[0-9]+)/(?P<order_id>[0-9]+)/$', views.update_order_info, name='shipping-address'),

    # api using rest-framework
    url(r'^api/products/$', views.ProductsList.as_view(), name='product-list'),
    url(r'^api/products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='product-detail'),
)


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'wishlists', views.WishListViewSet)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)