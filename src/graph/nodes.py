from src.agent.base_agent import agent_base
from src.db.crud import PostgreSQL
from src.evolution.client import EvolutionAPI
from src.graph.state import State
from src.graph.tools import Tools
from src.prompts.get_prompt import get_prompt

prompt_ai = get_prompt(prompt_name='prompt_01')

evo = EvolutionAPI()


class Nodes:
    @staticmethod
    def node_verify_user(state: State):
        number = state['number']

        exist = PostgreSQL.verify_user(number)

        if exist:
            print(f'✅ Usuário {number} já existe')
            return 'existent'
        else:
            print(f'🆕 Novo Usuário {number}')
            return 'new'

    @staticmethod
    def node_save_user(state: State):
        number = state['number']

        PostgreSQL.create_user(
            numero=number,
            nome='user',
            tipo_usuario='indefinido',
            turma_serie=None,
            metadata={},
        )

        return state

    @staticmethod
    def node_save_message_human(state: State):
        messages = state['messages']
        number = state['number']

        if messages:
            ultima = messages[-1]
            conteudo = ultima.content

            message_payload = {'type': 'human', 'content': conteudo}

            PostgreSQL.save_message(session_id=number, message=message_payload)

        return state

    @staticmethod
    def node_sender_message(state):
        messages = state['messages']
        number = state['number']

        last_message = messages[-1]
        text = last_message.content
        evo.sender_text(number=number, text=text)

        return state

    @staticmethod
    def node_save_message_ai(state: State):

        message = state['messages']
        number = state['number']

        if message:
            ultima = message[-1]
            conteudo = ultima.content

            message_payload = {'type': 'ai', 'content': conteudo}

            PostgreSQL.save_message(session_id=number, message=message_payload)

        return state

    @staticmethod
    def node_agente_assistente(state: State):

        return agent_base(
            state=state,
            prompt_ia=prompt_ai,
            llm_model=Tools.llm_with_tools,
            get_historico_func=PostgreSQL.get_historico,
        )

    @staticmethod
    def node_use_tools(state: State) -> str:
        last_message = state['messages'][-1]

        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print('🔍 Decisão: Chamar ferramentas.')
            return 'yes'
        else:
            print('✅ Decisão: Finalizar e responder.')
            return 'no'

    @staticmethod
    def node_execute_tools(state: State):
        print('🛠️ Executando ferramentas...')
        last_message = state['messages'][-1]

        response = Tools.tool_node.invoke({'messages': [last_message]})

        for msg in response['messages']:
            print(f'🔧 Resultado da ferramenta: {msg.content}')

        return {'mensagem': response['messages']}
