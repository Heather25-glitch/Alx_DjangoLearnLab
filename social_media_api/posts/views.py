from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, CustomUserSerializer
from notifications.models import Notification

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners to edit or delete their posts and comments.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions (GET, HEAD, OPTIONS) are allowed for any request.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed for the author of the post or comment.
        return obj.author == request.user

class FollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        request.user.following.add(user_to_follow)
        return Response({"message": "You are now following this user."}, status=status.HTTP_200_OK)

class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
        request.user.following.remove(user_to_unfollow)
        return Response({"message": "You have unfollowed this user."}, status=status.HTTP_200_OK)

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Optionally filter comments by post_id if provided in the request.
        """
        post_id = self.request.query_params.get("post_id")
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class FeedView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_query(self):
        following_users = self.request.user.following.all()
        return Post.objects.filter(author__in=following_users).order_by('-create_at')

class LikePostView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            Notification.objects.create(recipient=post.author, actor=request.user, verb='liked', target=post)
            return Response({'message': 'Post liked.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'You already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)

class UnlikePostView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=request.user, post=post)

        if like.exists():
            like.delete
            return Response({'message': 'Post unliked.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You have not liked this post.'}, status=status.HTTP_400_BAD_REQUEST)