from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import ComentarioForm


def lista_posts(request):
    posts = Post.objects.filter(status=Post.Status.PUBLICADO).order_by('-criado_em')
    return render(request, 'blog/lista_posts.html', {'posts': posts})


def detalhe_post(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLICADO)
    comentarios = post.comentarios.all().order_by('-criado_em')

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.save()
            return redirect('detalhe_post', slug=post.slug)
    else:
        form = ComentarioForm()

    return render(request, 'blog/detalhe_post.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
    })

