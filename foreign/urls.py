from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'foreign.views.map', name='home'),
    url(r'^about', 'foreign.views.about', name='about'),
    url(r'^methodology', 'foreign.views.methodology', name='methodology'),
    url(r'^incoming-fara', 'foreign.views.incoming_fara', name='incoming-fara'),
    # proposed arms form
    url(r'^form-profile/(\d+)', 'foreign.views.form_profile', name='form-profile'),
    url(r'^incoming-arms', 'foreign.views.incoming_arms', name='incoming-arms'),
    url(r'^arms-profile/(\d+)', 'foreign.views.arms_profile', name='arms-profile'),
    url(r'^client-profile/(\d+)', 'foreign.views.client_profile', name='client-profile'),
    url(r'^reg-profile/(\d+)', 'foreign.views.reg_profile', name='reg-profile'),
    url(r'^location-profile/(\d+)', 'foreign.views.location_profile', name='location-profile'),
    url(r'^recipient-profile/(\d+)', 'foreign.views.recipient_profile', name='recipient-profile'),
    url(r'^contact-table', 'foreign.views.contact_table', name='contact-table'),
    url(r'^payment-table', 'foreign.views.payment_table', name='payment-table'),
    url(r'^disbursement-table', 'foreign.views.disbursement_table', name='disbursement-table'),
    url(r'^contribution-table', 'foreign.views.contribution_table', name='contribution-table'),
    url(r'^registrants', 'foreign.views.reg_totals', name='registrants'),
    url(r'^clients', 'foreign.views.clients', name='clients'),
    url(r'^lobby-clients2013','foreign.views.lobby_clients', name='lobby-clients2013' ),
    url(r'^lobby-location2013', 'foreign.views.location13', name='location2013'),
    url(r'^search', 'foreign.views.search', name='search'),
    url(r'^more-search', 'foreign.views.search_more', name='more-search'),
    # to check status
    url(r'^test', 'foreign.views.test', name='test'),
    url(r'^map', 'foreign.views.map', name='map'),
    url(r'^generate_csv/(?P<model_str>(contact|contribution|payment|disbursement|client))$','foreign.views.generate_csv', name='generate-csv'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'foreign.views.not_found'
handler500 = 'foreign.views.error'
