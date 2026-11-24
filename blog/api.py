from django.db.models import Q
from rest_framework import viewsets
from .models import Blog, Post, Categoria, Comentario
from .serializers import (
    BlogSerializer, PostSerializer, CategoriaSerializer, ComentarioSerializer,
)


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.all().order_by('nome')
    serializer_class = BlogSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all().order_by('nome')
    serializer_class = CategoriaSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        qs = Post.objects.filter(status=Post.Status.PUBLICADO).order_by('-criado_em')
        q = self.request.query_params.get('q')
        categoria = self.request.query_params.get('categoria')
        blog = self.request.query_params.get('blog')
        if q:
            qs = qs.filter(Q(titulo__icontains=q))
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if blog:
            qs = qs.filter(blog_id=blog)
        return qs


class ComentarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comentario.objects.filter(
        post__status=Post.Status.PUBLICADO
    ).order_by('-criado_em')
    serializer_class = ComentarioSerializer