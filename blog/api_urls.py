from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register('blogs', api.BlogViewSet, basename='api-blog')
router.register('posts', api.PostViewSet, basename='api-post')
router.register('categorias', api.CategoriaViewSet, basename='api-categoria')
router.register('comentarios', api.ComentarioViewSet, basename='api-comentario')

urlpatterns = [
    path('', include(router.urls)),
]