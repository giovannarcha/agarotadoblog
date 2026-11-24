from django import forms
from django.utils.text import slugify
from .models import Comentario, Post, Blog


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['autor_nome', 'texto']
        widgets = {
            'autor_nome': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'texto': forms.Textarea(attrs={'placeholder': 'Deixe seu comentário...', 'rows': 4}),
        }


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['nome', 'descricao']

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome and Blog.objects.filter(slug=slugify(nome)).exists():
            raise forms.ValidationError('Já existe um blog com esse nome. Escolhe outro!')
        return nome


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['blog', 'titulo', 'conteudo', 'imagem_capa', 'categoria', 'tags']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['blog'].queryset = Blog.objects.filter(membros__usuario=user).distinct()

    def clean_conteudo(self):
        conteudo = self.cleaned_data.get('conteudo')
        if conteudo and len(conteudo) < 50:
            raise forms.ValidationError(
                'O conteúdo precisa ter pelo menos 50 caracteres. Escreva um pouco mais antes de salvar!'
            )
        return conteudo