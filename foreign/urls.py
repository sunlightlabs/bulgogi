from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'foreign.views.about', name='about'),
    url(r'^incoming_fara', 'foreign.views.incoming_fara', name='incoming-fara'),
    url(r'^form_profile/(\d+)', 'foreign.views.fara_profile', name='form-profile'),
    url(r'^incoming_arms', 'foreign.views.incoming_arms', name='incoming-arms'),
    url(r'^arms_profile/(\d+)', 'foreign.views.arms_profile', name='arms-profile'),
    # url(r'^foreign/', include('foreign.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
