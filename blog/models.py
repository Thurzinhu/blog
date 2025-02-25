from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique_for_date='publish'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )


    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]


    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )
    

    def get_similar_posts(self):
        post_tags_ids = self.tags.values_list('id', flat=True)
        return Post.published.filter(
            tags__in=post_tags_ids
        ).exclude(
            pk=self.id
        ).alias(
            similarity=Count('tags')
        ).order_by(
            '-similarity',
            '-publish'
        )


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField()
    name = models.CharField(max_length=80)
    body = models.TextField()
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    active = models.BooleanField(default=True)

    
    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]

    
    def __str__(self):
        return f"Comment by {self.name} on {self.post}"