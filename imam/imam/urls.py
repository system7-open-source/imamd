from django.conf.urls import patterns, include, url
from rapidsms.backends.kannel.views import KannelBackendView

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    # RapidSMS core URLs
    (r'^accounts/', include('rapidsms.urls.login_logout')),
    # url(r'^$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),
    # RapidSMS contrib app URLs
    (r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    # (r'^locations/', include('rapidsms.contrib.locations.urls')),
    # (r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    # (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    # (r'^registration/', include('rapidsms.contrib.registration.urls')),

    # Third party URLs
    (r'^selectable/', include('selectable.urls')),

    url(r'', include('webapp.urls')),
    url(r'^locations/', include('locations.urls')),
    url(r'inbound/kannel/$', KannelBackendView.as_view(backend_name='kannel')),
    url(r'backends/', include('rapidpro4rapidsms.urls')),
)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
