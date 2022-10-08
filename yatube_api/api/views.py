# TODO:  Напишите свой вариант
import sys

from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import Post, Group, Comment, Follow
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .permissions import AuthorOrReadOnly, ReadOnly
from .serializers import PostSerializer, CommentSerializer, FollowSerializer, \
    GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination
    permission_classes = (ReadOnly,)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('color', 'birth_year')
    search_fields = ('user',)

    def get_queryset(self):
        current_user = self.request.user
        new_queryset = Follow.objects.filter(user=current_user)
        return new_queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Http404 as e:
            return Response({'Error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        following = get_object_or_404(User,
                                      username=self.request.data.get(
                                          'following'))
        if Follow.objects.filter(user=self.request.user,
                                     following=following):
            raise Http404('Вы уже подписаны на этого автора.')
        if self.request.user == following:
            raise Http404('Вы не можете подписаться на себя.')
        serializer.save(user=self.request.user, following=following)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        new_queryset = Comment.objects.filter(post=post_id)
        return new_queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)
