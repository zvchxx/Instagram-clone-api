from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from post import models
from post import serializers
from post.paginations import CustomPagination

class PostView(generics.ListCreateAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return models.PostModel.objects.filter(user=self.request.user, parent__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.PostModel.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        post = self.get_object()
        if post.user != self.request.user:
            raise PermissionDenied("You can only edit your own post.")
        serializer.save()


class PostChildAPIView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        parent = self.request.query_params.get('parent')
        if parent is None:
            return []
        return models.PostModel.objects.filter(parent_id=parent)
    

class StoryViewSet(viewsets.ModelViewSet):
    queryset = models.StoryModel.objects.all()
    serializer_class = serializers.StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.StoryModel.objects.filter(user=self.request.user)
    

class BookMarkViewSet(viewsets.ModelViewSet):
    queryset = models.BookMarkModel.objects.all()
    serializer_class = serializers.BookMarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.BookMarkModel.objects.filter(user=self.request.user)
    

class PostCommentViewSet(viewsets.ModelViewSet):
    queryset = models.PostCommentModel.objects.all()
    serializer_class = serializers.PostCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.PostCommentModel.objects.filter(post__user=self.request.user)


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = models.PostLikeModel.objects.all()
    serializer_class = serializers.PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.PostLikeModel.objects.filter(user=self.request.user)
    

class StoryLikeViewSet(viewsets.ModelViewSet):
    queryset = models.StoryLikeModel.objects.all()
    serializer_class = serializers.StoryLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.StoryLikeModel.objects.filter(user=self.request.user)
    

class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = models.CommentLikeModel.objects.all()
    serializer_class = serializers.CommentLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.CommentLikeModel.objects.filter(user=self.request.user)