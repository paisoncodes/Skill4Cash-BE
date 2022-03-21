from .serializers import (
    RatingSerializer,
    CategorySerializer
)

from .models import (
    Rating,
    Category
)

from authentication.models import (
    ServiceProvider,
    User,
)

from rest_framework.permissions import IsAuthenticated
from src.permissions import IsOwnerOrReadOnly