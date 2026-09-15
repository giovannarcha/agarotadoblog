from django.db.models import Count
from .models import Post, Categoria

def sidebar_data(request):
    posts_recentes = Post.objects.filter(
        status=Post.Status.PUBLICADO
    ).order_by('-criado_em')[:5]

    posts_mais_comentados = Post.objects.filter(
        status=Post.Status.PUBLICADO
    ).annotate(
        num_comentarios=Count('comentarios')
    ).order_by('-num_comentarios')[:5]

    categorias = Categoria.objects.all()

    total_posts = Post.objects.filter(status=Post.Status.PUBLICADO).count()

    return {
        'sidebar_posts_recentes': posts_recentes,
        'sidebar_posts_comentados': posts_mais_comentados,
        'sidebar_categorias': categorias,
        'sidebar_total_posts': total_posts,
    }