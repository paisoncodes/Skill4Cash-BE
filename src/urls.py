from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from social_auth.views import (
    GoogleSocialAuthView,
)
from src.routers import router


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/google-auth/", GoogleSocialAuthView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("api/admin/", admin.site.urls),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
else:
    urlpatterns += [
        path(f"api/{settings.ADMIN_PATH}/", admin.site.urls),
    ]
