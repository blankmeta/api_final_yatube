from django.contrib.auth.models import User
from posts.models import Comment, Post, Group, Follow, Post
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    def validate(self, data):
        post_id = self.context['view'].kwargs.get('post_id')  # Не знаю,
        # насколько правильно вытаскивать kwargs из вью, но придумал только так
        # ¯\_(ツ)_/¯
        if not Post.objects.filter(pk=post_id):
            raise serializers.ValidationError('Пост не найден.')
        return data

    class Meta:
        fields = '__all__'
        model = Comment


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        required=False,
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())

    following = serializers.SlugRelatedField(queryset=User.objects.all(),
                                             slug_field='username')

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.')
        return data

    class Meta:
        fields = ('user', 'following',)
        model = Follow

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора.'
            )
        ]
