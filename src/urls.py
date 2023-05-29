from django.views.decorators.csrf import csrf_exempt
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from rest_framework import permissions
from django.conf import settings
from django.contrib import admin
from drf_yasg import openapi
from utils.views import get_lgas, get_states, populate_states_and_lga

schema_view = get_schema_view(
    openapi.Info(
        title="Skill4Cash API",
        default_version="1.0.0",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/', include('services.urls')),
    # path('api/v1/', include('chat.urls')),
    path('api/v1/get-states', get_states),
    path('api/v1/get-lgas', get_lgas),
    path('api/v1/add-states-and-lgas', populate_states_and_lga)
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        csrf_exempt(schema_view.without_ui(cache_timeout=0)),
        name="schema-json",
    ),
    re_path(
        r"^api/v1/docs/$",
        csrf_exempt(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", csrf_exempt(schema_view.with_ui("redoc", cache_timeout=0)), name="schema-redoc"
    ),
]