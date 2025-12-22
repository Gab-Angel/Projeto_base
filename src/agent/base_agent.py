import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

load_dotenv()

# CONEXÃO COM A GROQ
llm_groq = ChatGroq(
    api_key=os.getenv('GROQ_API_KEY'),
    model_name='openai/gpt-oss-120b',
    temperature=0,
)

# MODELS
# openai/gpt-oss-120b
# llama-3.3-70b-versatile


def agent_base(state, prompt_ia: str, llm_model, get_historico_func):
    numero = state['number']

    # Recupera histórico com função injetada (agora síncrona)
    mensagens_historico = get_historico_func(numero)

    # Junta com mensagens do state (mensagem atual)
    mensagens_historico.extend(state['messages'])

    print('🤖 Agente pensando...')

    system_prompt = (
        f'{prompt_ia}\n\n'
        f'IMPORTANTE: O número do usuário é {numero}. '
        f'Use sempre este número ao chamar ferramentas.'
    )

    messages = [SystemMessage(content=system_prompt)] + mensagens_historico

    # Chamada do modelo
    response = llm_model.invoke(messages)

    return {'messages': [response]}
