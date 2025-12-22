from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

from src.agent.audio_transcription import audio_transcription
from src.db.table import create_tables
from src.graph.workflow import graph
from src.redis.buffer import adicionar_ao_buffer, iniciar_ouvinte_background


async def processar_mensagens_agrupadas(numero: str, texto_final: str):

    try:
        print(f'📦 Processando buffer para: {numero}')
        print(f'💬 Texto agrupado: {texto_final}')

        entrada = {
            'messages': [HumanMessage(content=texto_final)],
            'number': numero,
        }

        resultado = graph.invoke(entrada)

        if resultado.get("messages"):
            ultima_mensagem = resultado["messages"][-1]
            
            # Pega a resposta do AI
            if hasattr(ultima_mensagem, 'content'):
                resposta_ia = ultima_mensagem.content
            else:
                resposta_ia = "Sem resposta"
            
            # Pega metadados de uso de tokens e performance
            metadata = getattr(ultima_mensagem, 'response_metadata', {})
            token_usage = metadata.get('token_usage', {})
            
            print(f"✅ Agente processou com sucesso para {numero}")
            print(f"\n{'='*60}")
            print(f"📝 Resposta IA: {resposta_ia}")
            print(f"\n📊 Métricas:")
            print(f"   • Tokens entrada: {token_usage.get('prompt_tokens', 'N/A')}")
            print(f"   • Tokens saída: {token_usage.get('completion_tokens', 'N/A')}")
            print(f"   • Total tokens: {token_usage.get('total_tokens', 'N/A')}")
            print(f"   • Tempo total: {metadata.get('total_time', 'N/A'):.3f}s" if isinstance(metadata.get('total_time'), (int, float)) else f"   • Tempo total: {metadata.get('total_time', 'N/A')}")
            print(f"   • Modelo: {metadata.get('model_name', 'N/A')}")
            print(f"   • Motivo finalização: {metadata.get('finish_reason', 'N/A')}")
            print(f"{'='*60}\n")


    except Exception as e:
        print(f'❌ Erro ao processar mensagens para {numero}: {e}')
        print(
            f'Entrada que causou erro: numero={numero}, texto={texto_final}\n'
        )


@asynccontextmanager
async def lifespan(app: FastAPI):

    print('🚀 Inicializando aplicação...')

    create_tables()
    print('🟢 Banco pronto!')

    iniciar_ouvinte_background(processar_mensagens_agrupadas)

    print('✅ Sistema de buffer pronto!\n')

    yield  # Aplicação roda aqui

    print('🛑 Encerrando aplicação...')


app = FastAPI(lifespan=lifespan)


@app.post('/webhook')
async def webhook(request: Request):

    try:
        data = await request.json()
        messageType = data['data'].get('messageType')

        if data:
            # ========== EXTRAI O TIPO DE MENSAGEM ==========
            if messageType == 'conversation':
                # Mensagem de texto normal
                message = data['data']['message'].get('conversation')

            elif messageType == 'audioMessage':
                # Mensagem de áudio - precisa transcrição
                base64 = data['data']['message'].get('base64')
                print('Processando Audio...')
                result = audio_transcription(audio_base64=base64)
                message = result['text']

            else:
                # Tipo de mensagem não suportado
                message = None

            # ========== EXTRAI O NÚMERO DO USUÁRIO ==========
            remoteJid = data['data']['key'].get('remoteJid')
            number = remoteJid.split('@')[0]

            # ========== ADICIONA AO BUFFER ==========
            print(f'📲 Mensagem de: {number}')
            print(f'💬 Conteúdo: {message}')

            adicionar_ao_buffer(number, message)

            print(f'➕ Mensagem adicionada ao buffer para {number}\n')

            return JSONResponse(
                content={'status': 'mensagem adicionada ao buffer'},
                status_code=200,
            )
        else:
            print('⚠️ Payload do webhook não continha os dados esperados.')
            return JSONResponse(
                content={'status': 'payload invalido'}, status_code=400
            )

    except Exception as e:
        print(f'❌ Erro no webhook: {e}')
        raise HTTPException(status_code=500, detail='erro interno')


@app.get('/health')
async def health_check():
    """
    Rota simples para verificar se a app está rodando.
    Útil para monitoramento.
    """
    return {'status': 'ok', 'message': 'Aplicação rodando com sucesso'}
