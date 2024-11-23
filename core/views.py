# Create your views here.


from django.shortcuts import render

from core.ia.main import AssistentTranscricao


def index(request):
    ai_response = ''
    if request.method == 'POST':
        url_video = request.POST.get('url_video')
        query_user = request.POST.get('query_user')
        model_class = request.POST.get('model_class')

        assistent = AssistentTranscricao(model_class=model_class)
        # query_user = 'sumarize de forma clara de entender'
        language = ['pt', 'pt-BR', 'en']
        ai_response = assistent.interpret_video(url_video, query_user, language)

    return render(request, 'index.html', {'ai_response': ai_response})
