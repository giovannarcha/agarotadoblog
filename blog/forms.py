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

    def clean_conteudo(self):
        conteudo = self.cleaned_data.get('conteudo')
        if conteudo and len(conteudo) < 50:
            raise forms.ValidationError(
                'O conteúdo precisa ter pelo menos 50 caracteres. Escreva um pouco mais antes de salvar!'
            )
        return conteudo