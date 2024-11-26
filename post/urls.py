from django.urls import path, include

from post import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'stories', views.StoryViewSet)
router.register(r'marks', views.BookMarkViewSet)
router.register(r'comments', views.PostCommentViewSet)
router.register(r'like-posts', views.PostLikeViewSet)
router.register(r'like-stories', views.StoryLikeViewSet)
router.register(r'like-comments', views.CommentLikeViewSet)

urlpatterns = [
    path('', views.PostView.as_view()),
    path('post/<int:pk>/', views.PostDetailView.as_view()),
    path('child/', views.PostChildAPIView.as_view()),

    #router urls
    path('', include(router.urls)),
]    