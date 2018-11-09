from django.conf.urls import url
from . import views
app_name = 'receipt'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^upload_receipt/$', views.upload_receipt, name='upload_receipt'),
    url(r'^(?P<receipt_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^update_ocr/(?P<receipt_id>[0-9]+)$', views.update_ocr, name='update_ocr'),
]
