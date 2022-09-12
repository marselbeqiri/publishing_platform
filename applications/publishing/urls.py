from rest_framework.routers import DefaultRouter

from applications.publishing.views.post import PostViewSet

router = DefaultRouter()
router.register('post', PostViewSet, basename='post')

urlpatterns = router.urls
