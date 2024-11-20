# -*- coding: utf-8 -*-
"""Curso LLMs Projeto 01 - Transcrição e compreensão de vídeos"""

import io
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.llms import HuggingFaceHub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


class AssistentTranscricao:
    def __init__(self, model_class):
        self.model_class = model_class

        self._setup_environment_variables(self.model_class)

    def _setup_environment_variables(self, provedor_ai):  # noqa: PLR6301
        load_dotenv()

        # os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass()

        if provedor_ai == 'openai':
            open_api_key = os.getenv('OPEN_API_KEY')
            os.environ['OPENAI_API_KEY'] = open_api_key
        else:
            groq_api_key = os.getenv('GROQ_API_KEY')
            os.environ['GROQ_API_KEY'] = groq_api_key

    def format_transcricao(self, infos, transcricao: str) -> str:  # noqa: PLR6301
        infos_video = f"""Informações do vídeo:

        Título: {infos[0].metadata['title']}
        Autor: {infos[0].metadata['author']}
        Data: {infos[0].metadata['publish_date'][:10]}
        URL: https://www.youtube.com/watch?v={infos[0].metadata['source']}

        Transcrição: {transcricao}
        """
        return infos_video

    def salve_file_transcricao(self, infos, infos_formated: str):  # noqa: PLR6301
        with io.open('transcricao.txt', 'w', encoding='utf-8') as f:
            for doc in infos:
                f.write(infos_formated)

    def model_hf_hub(  # noqa: PLR6301
        self, model='meta-llama/Meta-Llama-3-8B-Instruct', temperature=0.1
    ):
        llm = HuggingFaceHub(
            repo_id=model,
            model_kwargs={
                'temperature': temperature,
                'return_full_text': False,
                'max_new_tokens': 1024,
            },
        )
        return llm

    def model_openai(self, model='gpt-4o-mini', temperature=0.1):  # noqa: PLR6301
        llm = ChatOpenAI(model=model, temperature=temperature)
        return llm

    def model_groq(  # noqa: PLR6301
        self, model='llama3-groq-70b-8192-tool-use-preview', temperature=0.1
    ):
        llm = ChatGroq(model=model, temperature=temperature)
        return llm

    def model_ollama(self, model='phi3', temperature=0.1):  # noqa: PLR6301
        llm = ChatOllama(model=model, temperature=temperature)
        return llm

    def llm_chain(self):
        system_prompt = (
            'Você é um assistente virtual prestativo e deve responder a '
            + 'uma consulta com base na transcrição de um vídeo, que será'
            + ' fornecida abaixo.'
        )

        inputs = 'Consulta: {consulta} \n Transcrição: {transcricao}'

        if self.model_class.startswith('hf'):
            user_prompt = (
                '<|begin_of_text|><|start_header_id|>user<|end_header_id|>'
                + '\n{}<|eot_id|><|start_header_id|>assistant<|end_header_id|>'.format(
                    inputs
                )
            )
        else:
            user_prompt = '{}'.format(inputs)

        prompt_template = ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('user', user_prompt),
        ])

        if self.model_class == 'hf_hub':
            llm = self.model_hf_hub()
        elif self.model_class == 'openai':
            llm = self.model_openai()
        elif self.model_class == 'ollama':
            llm = self.model_ollama()
        elif self.model_class == 'groq':
            llm = self.model_groq()

        chain = prompt_template | llm | StrOutputParser()

        return chain

    def get_video_info(self, url_video, language='pt', translation=None):  # noqa: PLR6301
        video_loader = YoutubeLoader.from_youtube_url(
            url_video,
            # add_video_info=True,
            language=language,
            translation=translation,
        )

        infos = video_loader.load()[0]
        # print("aqui", infos)
        metadata = infos.metadata
        transcript = infos.page_content

        return transcript, metadata

    def interpret_video(self, url, query='resuma', language='pt', translation=None):
        try:
            transcript, metadata = self.get_video_info(url, language, translation)  # noqa: F841

            chain = self.llm_chain()

            res = chain.invoke({'transcricao': transcript, 'consulta': query})
            print(res)
            # return res
        except Exception as e:
            print('Erro ao carregar transcrição')
            print(e)


# url_video = "https://www.youtube.com/watch?v=3LHSyha0xN0"
url_video = input('Informe a url do video: ')
query_user = 'sumarize de forma clara de entender'
model_class = 'groq'
language = ['pt', 'pt-BR', 'en']

assitent = AssistentTranscricao(model_class=model_class)
assitent.interpret_video(url_video, query_user, language)
