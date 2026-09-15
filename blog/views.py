from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import ComentarioForm, PostForm
from .models import Post, Categoria


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


@login_required
def meus_posts(request):
    posts = Post.objects.filter(autor=request.user).order_by('-criado_em')
    return render(request, 'blog/meus_posts.html', {'posts': posts})


@login_required
def criar_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            form.save_m2m()
            return redirect('meus_posts')
    else:
        form = PostForm()
    return render(request, 'blog/form_post.html', {'form': form, 'titulo_pagina': 'Novo post'})


@login_required
def editar_post(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('meus_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/form_post.html', {'form': form, 'titulo_pagina': 'Editar post'})


@login_required
def avancar_status(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    if post.status == Post.Status.RASCUNHO:
        post.enviar_para_revisao()
    elif post.status == Post.Status.EM_REVISAO:
        post.publicar()
    elif post.status == Post.Status.PUBLICADO:
        post.arquivar()
    return redirect('meus_posts')

def posts_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    posts = Post.objects.filter(
        status=Post.Status.PUBLICADO,
        categoria=categoria
    ).order_by('-criado_em')
    return render(request, 'blog/lista_posts.html', {
        'posts': posts,
        'categoria_filtrada': categoria,
    })