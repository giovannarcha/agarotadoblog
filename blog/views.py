from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from .models import Post, Categoria, Blog, Membro, Comentario
from .forms import ComentarioForm, PostForm, BlogForm


def _pode_avancar(user, post):
    """Regra dos papéis: quem pode mover o post para o próximo estado."""
    if post.status == Post.Status.RASCUNHO:
        return post.autor_id == user.id
    if post.status in (Post.Status.EM_REVISAO, Post.Status.PUBLICADO):
        return post.blog is not None and post.blog.papel_de(user) in (Membro.Papel.DONO, Membro.Papel.EDITOR)
    return False


def lista_posts(request):
    posts = Post.objects.filter(status=Post.Status.PUBLICADO).order_by('-criado_em')

    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')

    if query:
     posts = posts.filter(Q(titulo__icontains=query))
    if categoria_id:
        posts = posts.filter(categoria_id=categoria_id)

    return render(request, 'blog/lista_posts.html', {
        'posts': posts,
        'query': query,
        'categoria_selecionada': categoria_id,
        'categorias': Categoria.objects.all(),
    })


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


def lista_blogs(request):
    blogs = Blog.objects.annotate(
        num_posts=Count('posts', filter=Q(posts__status=Post.Status.PUBLICADO))
    ).order_by('nome')
    return render(request, 'blog/lista_blogs.html', {'blogs': blogs})


def detalhe_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    posts = Post.objects.filter(blog=blog, status=Post.Status.PUBLICADO).order_by('-criado_em')

    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')

    if query:
        posts = posts.filter(Q(titulo__icontains=query))
    if categoria_id:
        posts = posts.filter(categoria_id=categoria_id)

    return render(request, 'blog/detalhe_blog.html', {
        'blog': blog,
        'posts': posts,
        'query': query,
        'categoria_selecionada': categoria_id,
        'categorias': Categoria.objects.all(),
    })


@login_required
def criar_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.dono = request.user
            blog.save()
            Membro.objects.create(usuario=request.user, blog=blog, papel=Membro.Papel.DONO)
            return redirect('detalhe_blog', slug=blog.slug)
    else:
        form = BlogForm()
    return render(request, 'blog/form_post.html', {'form': form, 'titulo_pagina': 'Criar meu blog'})


@login_required
def meus_posts(request):
    posts = list(Post.objects.filter(autor=request.user).order_by('-criado_em'))
    for p in posts:
        p.pode_avancar = _pode_avancar(request.user, p)
    return render(request, 'blog/meus_posts.html', {'posts': posts})


@login_required
def revisao(request):
    blogs_ids = Membro.objects.filter(
        usuario=request.user,
        papel__in=[Membro.Papel.DONO, Membro.Papel.EDITOR],
    ).values_list('blog_id', flat=True)
    posts = Post.objects.filter(
        blog_id__in=blogs_ids, status=Post.Status.EM_REVISAO
    ).order_by('criado_em')
    return render(request, 'blog/revisao.html', {'posts': posts})


@login_required
def criar_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            form.save_m2m()
            return redirect('meus_posts')
    else:
        form = PostForm(user=request.user)
    return render(request, 'blog/form_post.html', {'form': form, 'titulo_pagina': 'Novo post'})


@login_required
def editar_post(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('meus_posts')
    else:
        form = PostForm(instance=post, user=request.user)
    return render(request, 'blog/form_post.html', {'form': form, 'titulo_pagina': 'Editar post'})


@login_required
def avancar_status(request, slug):
    post = get_object_or_404(Post, slug=slug)
    destino = request.POST.get('next', 'meus_posts')
    if destino not in ('meus_posts', 'revisao'):
        destino = 'meus_posts'

    if request.method != 'POST':
        return redirect(destino)

    if not _pode_avancar(request.user, post):
        return HttpResponseForbidden('Você não tem permissão para fazer isso neste blog.')

    if post.status == Post.Status.RASCUNHO:
        post.enviar_para_revisao()
    elif post.status == Post.Status.EM_REVISAO:
        post.publicar()
    elif post.status == Post.Status.PUBLICADO:
        post.arquivar()
    return redirect(destino)


@login_required
def dashboard(request):
    if request.user.is_superuser:
        blogs = Blog.objects.all()
    else:
        blogs = Blog.objects.filter(
            membros__usuario=request.user,
            membros__papel__in=[Membro.Papel.DONO, Membro.Papel.EDITOR],
        ).distinct()

    posts = Post.objects.filter(blog__in=blogs)

    por_status = [
        {'nome': rotulo, 'total': posts.filter(status=valor).count()}
        for valor, rotulo in Post.Status.choices
    ]

    mais_comentados = posts.filter(
        status=Post.Status.PUBLICADO
    ).annotate(
        num_comentarios=Count('comentarios')
    ).order_by('-num_comentarios', '-criado_em')[:5]

    resumo_blogs = blogs.annotate(
        total_posts=Count('posts', distinct=True),
        total_comentarios=Count('posts__comentarios', distinct=True),
    )

    return render(request, 'blog/dashboard.html', {
        'total_blogs': blogs.count(),
        'total_posts': posts.count(),
        'total_comentarios': Comentario.objects.filter(post__in=posts).count(),
        'por_status': por_status,
        'mais_comentados': mais_comentados,
        'resumo_blogs': resumo_blogs,
    })


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


def welcome(request):
    posts_recentes = Post.objects.filter(
        status=Post.Status.PUBLICADO
    ).order_by('-criado_em')[:4]

    posts_arquivo = Post.objects.filter(
        status=Post.Status.PUBLICADO
    ).annotate(
        num_comentarios=Count('comentarios')
    ).order_by('-num_comentarios', '-criado_em')

    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')

    if query:
        posts_arquivo = posts_arquivo.filter(
            Q(titulo__icontains=query) | Q(conteudo__icontains=query)
       )
    if categoria_id:
        posts_arquivo = posts_arquivo.filter(categoria_id=categoria_id)

    paginator = Paginator(posts_arquivo, 6)
    numero_pagina = request.GET.get('page')
    pagina_atual = paginator.get_page(numero_pagina)

    return render(request, 'blog/welcome.html', {
        'posts_recentes': posts_recentes,
        'pagina_atual': pagina_atual,
        'categorias': Categoria.objects.all(),
        'query': query,
        'categoria_selecionada': categoria_id,
})