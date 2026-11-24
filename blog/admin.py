from django.contrib import admin
from .models import Categoria, Tag, Post, Comentario, Blog, Membro


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dono', 'criado_em')
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'blog', 'papel')
    list_filter = ('blog', 'papel')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'blog', 'categoria', 'status', 'criado_em')
    list_filter = ('status', 'blog', 'categoria')
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ('tags',)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('post', 'autor_nome', 'criado_em')