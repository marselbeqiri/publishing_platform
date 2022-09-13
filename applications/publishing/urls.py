from rest_framework.routers import DefaultRouter

from applications.publishing.views.post import PostViewSet
from applications.publishing.views.subscribe import MemberViewSet

router = DefaultRouter()
router.register('members', MemberViewSet, basename='member')
router.register('post', PostViewSet, basename='post')

urlpatterns = router.urls
