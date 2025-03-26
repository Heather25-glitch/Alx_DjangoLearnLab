from rest_framework import viewsets, status
from rest_framework import permissions
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment, Like
from rest_framework.permissions import BasePermission
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the author of the post
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    def get_queryset(self):
        queryset = Post.objects.all()
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset
    


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        # Get the post ID from the request data and check if it exists
        post_id = self.request.data.get('post')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post does not exist")
        # Save comment with current user as author and associated post
        serializer.save(author=self.request.user, post=post)
    
    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    
class PostPagination(PageNumberPagination):
    page_size = 10
    
class FeedView(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
    
    def get_queryset(self):
        following_users = self.request.user.following.all()
        return Post.objects.filter(author__in=following_users).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, pk):
    """
    Handle liking a post
    """
    post = get_object_or_404(Post, pk=pk)  
    # Check if user has already liked the post
    like, created = Like.objects.get_or_create(
        user=request.user, 
        post=post
    )
       
    if not created:
        return Response(
            {'detail': 'You have already liked this post'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a notification for the post owner
    if request.user != post.author:
        Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb='liked your post',
            content_type=ContentType.objects.get_for_model(post),
            object_id=post.id
        )
    
    return Response({
        'detail': 'You liked this post', 
        'likes_count': post.likes.count()
    }, status=status.HTTP_201_CREATED)
    
 
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unlike_post(request, pk):
    """
    Handle unliking a post
    """
    post = get_object_or_404(Post, pk=pk)
    
    try:
        like = Like.objects.get(user=request.user, post=post)
        like.delete()
        
        return Response({
            'detail': 'You have unliked this post', 
            'likes_count': post.likes.count()
        }, status=status.HTTP_200_OK)
    
    except Like.DoesNotExist:
        return Response(
            {'detail': 'You have not liked this post'}, 
            status=status.HTTP_400_BAD_REQUEST
        )    
               