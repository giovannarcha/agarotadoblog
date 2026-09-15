from django import forms
from .models import Comentario, Post


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['autor_nome', 'texto']
        widgets = {
            'autor_nome': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'texto': forms.Textarea(attrs={'placeholder': 'Deixe seu comentário...', 'rows': 4}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'imagem_capa', 'categoria', 'tags']

