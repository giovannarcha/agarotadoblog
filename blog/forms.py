from django import forms
from .models import Comentario


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['autor_nome', 'texto']
        widgets = {
            'autor_nome': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'texto': forms.Textarea(attrs={'placeholder': 'Deixe seu comentário...', 'rows': 4}),
        }