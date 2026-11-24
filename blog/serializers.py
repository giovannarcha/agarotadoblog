from rest_framework import serializers
from .models import Blog, Post, Categoria, Comentario


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug']


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['id', 'post', 'autor_nome', 'texto', 'criado_em']


class BlogSerializer(serializers.ModelSerializer):
    dono = serializers.StringRelatedField()

    class Meta:
        model = Blog
        fields = ['id', 'nome', 'slug', 'descricao', 'dono', 'criado_em']


class PostSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField()
    blog = serializers.StringRelatedField()
    categoria = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    total_comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'titulo', 'slug', 'conteudo', 'autor', 'blog',
                  'categoria', 'tags', 'status', 'criado_em', 'total_comentarios']

    def get_total_comentarios(self, obj):
        return obj.comentarios.count()