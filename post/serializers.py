from rest_framework import serializers
from post import models


class PostSerializer(serializers.ModelSerializer):
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = models.PostModel
        fields = ['id', 'user', 'opisanya', 'created_at', 'updated_at', 'image', 'video', 'child_count']
        extra_kwargs = {
            'parent': {'required': False},
        }

    def get_child_counts(self, obj):
        return obj.children.count()

    def validate(self, attrs):
        image = attrs.get('image')
        video = attrs.get('video')

        if image and video:
            raise serializers.ValidationError("You can only upload either an image or a video, not both.")
        
        if not image and not video:
            raise serializers.ValidationError("You must upload either an image or a video.")
        
        return attrs
    

class StorySerializer(serializers.ModelSerializer):
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    tags_count = serializers.ReadOnlyField()
    marks_count = serializers.ReadOnlyField()

    class Meta:
        model = models.StoryModel
        fields = ['id', 'user', 'photo', 'video', 'description', 'is_cached', 'views', 
                  'likes_count', 'comments_count', 'tags_count', 'marks_count']
        read_only_fields = ['id', 'user']


class BookMarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BookMarkModel
        fields = ['id', 'user', 'post', 'story']
    

class PostCommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.ReadOnlyField()

    class Meta:
        model = models.PostCommentModel
        fields = ['id', 'comment', 'post', 'user', 'likes_count', 'parent']
        read_only_fields = ['id', 'user', 'post']
        extra_kwargs = {
            'parent': {'required': False},
        }


class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PostLikeModel
        fields = ['id', 'story', 'user']

class StoryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoryLikeModel
        fields = ['id', 'story', 'user']


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommentLikeModel
        fields = ['id', 'comment', 'user']