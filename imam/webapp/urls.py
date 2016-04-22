from django.conf.urls import include, patterns, url
from rapidsms.backends.kannel.views import KannelBackendView
from tastypie.api import Api

from locations.api.resources import NonSiteLocationNameResource
from core.api.resources import LowStockResource, StockOutResource
from messagebox.api.resources import MessageResource
import views


v1_api = Api(api_name='v1')
v1_api.register(LowStockResource())
v1_api.register(StockOutResource())
v1_api.register(MessageResource())
v1_api.register(NonSiteLocationNameResource())

urlpatterns = patterns(
    '',
    url(r'^$', 'webapp.views.dashboard', name='dashboard'),
    url(r'^chart-data/?$',
        views.DashboardChartDataView.as_view(),
        name='dashboard_chart'),

    url(r'^messages/?$', views.MessageListView.as_view(),
        name='messages'),
    url(r'^reports/?$',
        views.ProgramReportListView.as_view(),
        name='reports'),
    url(r'^report/(?P<pk>\d+)/?$',
        views.ProgramReportEditView.as_view(),
        name='report_edit'),
    url(
        r'^report/(?P<obj_id>\d+)/history/(?P<version_id>\d+)/?$',
        views.ProgramReportHistoryDetailView.as_view(),
        name='report_history'),
    url(
        r'^report/(?P<obj_id>\d+)/history/(?P<version_id>\d+)/revert/?$',
        views.ProgramReportRevertView.as_view(),
        name='report_revert'),
    url(r'^sites/?$', views.SiteListView.as_view(),
        name='sites'),
    url(r'^stocks/?$', views.StockReportListView.as_view(),
        name='stock_reports'),
    url(r'^stockout-alerts/?$',
        views.StockOutReportListView.as_view(),
        name='stockout_alerts'),
    url(r'^personnel/?$', views.PersonnelListView.as_view(),
        name='personnel'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^accounts/login/?$', 'webapp.views.signin',
        name='signin'),
    url(r'^accounts/logout/?$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='signout'),
    url(r'^iso_calendar/$', views.ISOCalendarView.as_view(),
        name='iso_calendar'),
    url(r'^pdf_forms/$', views.PdfFormListView.as_view(),
        name='pdf_forms'),
    url(r'^kannel/',
        include('rapidsms.backends.kannel.urls')),
    url(r"^backend/kannel-fake-smsc/$",
        KannelBackendView.as_view(
            backend_name="kannel-fake-smsc")),
)
