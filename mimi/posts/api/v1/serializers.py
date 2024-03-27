from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from mimi.accounts.api.v1.serializers import UserSerializer
from django.utils import timezone
from mimi.posts.models import (
    Post,
    PostImage,
    PostReaction,
    CommentToPost,
    CommentToPostImages,
    CommentToPostReaction,
)

User = get_user_model()


class ReactionToPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ["user_post", "user_that_react", "reaction"]

    def create(self, validated_data):
        validated_data["user_that_react"] = self.context["request"].user
        post_reaction_obj, created = PostReaction.objects.get_or_create(
            user_post=validated_data["user_post"],
            user_that_react=self.context["request"].user,
            defaults={
                "user_that_react": self.context["request"].user,
                "reaction": validated_data["reaction"],
            },
        )

        if not created:
            post_reaction_obj.reaction = validated_data["reaction"]
            post_reaction_obj.save()
            return post_reaction_obj

        return created


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "post_image"]


class PostSerializer(serializers.ModelSerializer):
    # post_reactions = ReactionToPostSerializer(many=True)

    images = PostImageSerializer(many=True)
    post_images = serializers.ListField(
        child=serializers.ImageField(required=False, allow_empty_file=True),
        required=False,
    )

    class Meta:
        model = Post
        fields = ["id", "post_details", "post_state", "images", "post_images"]

    @transaction.atomic
    def create(self, validated_data):
        post_details = validated_data["post_details"]
        post_state = validated_data.pop("post_state", "draft")

        post_obj = Post.objects.create(
            user=self.context["request"].user,
            post_details=post_details,
            post_state=post_state,
        )

        post_images = validated_data.pop("post_images", None)

        if post_images is not None:
            for post_image in post_images:
                PostImage.objects.create(post=post_obj, post_image=post_image)

        return post_obj


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["post_details", "post_state"]

    def update(self, instance, validated_data):
        if "post_state" in validated_data:
            instance.created_at, instance.last_modified_at = (
                timezone.now(),
                timezone.now(),
            )
            instance.save()
        return super().update(instance, validated_data)


class CommentToPostImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentToPostImages
        fields = [
            # "comment_to_post",
            "post_image"
        ]


class CommentToPostSerializer(serializers.ModelSerializer):
    comment_to_post_images = CommentToPostImagesSerializer(read_only=True, many=True)
    user_that_comment = UserSerializer(read_only=True)
    uploaded_comment_to_post_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False), max_length=2
    )

    class Meta:
        model = CommentToPost
        fields = [
            "id",
            "post",
            "user_that_comment",
            "comment",
            "edited",
            "comment_to_post_images",
            "uploaded_comment_to_post_images",
        ]

    @transaction.atomic
    def create(self, validated_data):
        uploaded_comment_to_post_images = validated_data.pop(
            "uploaded_comment_to_post_images", None
        )

        comment_to_post_obj = CommentToPost.objects.create(
            post=validated_data["post"],
            comment=validated_data["comment"],
            user_that_comment=self.context["request"].user,
        )

        if uploaded_comment_to_post_images is not None:
            for comment_to_post_image in uploaded_comment_to_post_images:
                CommentToPostImages.objects.create(
                    comment_to_post=comment_to_post_obj,
                    post_image=comment_to_post_image,
                )
        return comment_to_post_obj


class CommentToPostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentToPostReaction
        fields = ["comment_to_post", "user_that_react", "reaction"]

    def create(self, validated_data):
        return super().create(validated_data)


class ReplyToCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentToPost
        fields = [
            "post",
            "parent_comment",
            "comment",
        ]

    def create(self, validated_data):
        reply = CommentToPost.objects.create(
            comment=validated_data["comment"],
            post=validated_data["post"],
            parent_comment=validated_data["parent_comment"],
            user_that_comment=self.context["request"].user,
        )
        return reply


class RepliesToCommentSerializer(serializers.ModelSerializer):
    # replies_to_comment = ReplyToCommentSerializer()
    user_that_comment = UserSerializer()

    class Meta:
        model = CommentToPost
        fields = ["id", "comment", "user_that_comment"]

    def get_field_names(self, declared_fields, info):
        return super().get_field_names(declared_fields, info)
