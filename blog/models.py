from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Tag(models.Model):
    nome = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Blog(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descricao = models.TextField(blank=True)
    dono = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def papel_de(self, user):
        membro = self.membros.filter(usuario=user).first()
        return membro.papel if membro else None

    def __str__(self):
        return self.nome


class Membro(models.Model):
    class Papel(models.TextChoices):
        DONO = 'DONO', 'Dono'
        EDITOR = 'EDITOR', 'Editor'
        AUTOR = 'AUTOR', 'Autor'

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participacoes')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='membros')
    papel = models.CharField(max_length=10, choices=Papel.choices, default=Papel.AUTOR)

    class Meta:
        unique_together = ('usuario', 'blog')

    def __str__(self):
        return f'{self.usuario.username} - {self.get_papel_display()} em {self.blog.nome}'


class Post(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        EM_REVISAO = 'EM_REVISAO', 'Em revisão'
        PUBLICADO = 'PUBLICADO', 'Publicado'
        ARQUIVADO = 'ARQUIVADO', 'Arquivado'

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    conteudo = models.TextField()
    imagem_capa = models.ImageField(upload_to='capas/', blank=True, null=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, related_name='posts')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def enviar_para_revisao(self):
        if self.status == self.Status.RASCUNHO:
            self.status = self.Status.EM_REVISAO
            self.save()

    def publicar(self):
        if self.status == self.Status.EM_REVISAO:
            self.status = self.Status.PUBLICADO
            self.save()

    def arquivar(self):
        if self.status == self.Status.PUBLICADO:
            self.status = self.Status.ARQUIVADO
            self.save()

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor_nome = models.CharField(max_length=100)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return f'Comentário de {self.autor_nome} em {self.post.titulo}'