from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_posts, name='lista_posts'),
    path('post/<slug:slug>/', views.detalhe_post, name='detalhe_post'),
    path('meus-posts/', views.meus_posts, name='meus_posts'),
    path('meus-posts/novo/', views.criar_post, name='criar_post'),
    path('meus-posts/<slug:slug>/editar/', views.editar_post, name='editar_post'),
    path('meus-posts/<slug:slug>/avancar/', views.avancar_status, name='avancar_status'),
    path('categoria/<int:categoria_id>/', views.posts_por_categoria, name='posts_por_categoria'),
    path('welcome/', views.welcome, name='welcome'),
]

