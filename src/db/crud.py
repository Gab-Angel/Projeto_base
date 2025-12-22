import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.db.conection import get_vector_conn


class PostgreSQL:
    @staticmethod
    def verify_user(number: str) -> bool:
        conn = get_vector_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT numero
                FROM users
                WHERE numero = %s
            """,
                (number,),
            )

            row = cursor.fetchone()
            return row is not None

        except Exception as e:
            print(f'❌ Erro ao verificar usuário: {e}')
            return False

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create_user(
        numero: str,
        nome: str,
        tipo_usuario: str,
        turma_serie: str | None = None,
        metadata: dict = None,
    ):
        if metadata is None:
            metadata = {}

        conn = get_vector_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (numero, nome, tipo_usuario, turma_serie, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (numero) DO NOTHING
            """,
                (
                    numero,
                    nome,
                    tipo_usuario,
                    turma_serie,
                    json.dumps(metadata),
                ),
            )
            conn.commit()
            print(f'✅ Usuário {numero} salvo com sucesso')

        except Exception as e:
            print(f'❌ Erro ao salvar usuário: {e}')

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_user(
        numero: str,
        nome: str | None,
        tipo_usuario: str | None,
        turma_serie: str | None,
    ):
        conn = get_vector_conn()
        cursor = conn.cursor()  # ← adicionar cursor

        try:
            cursor.execute(
                """
                UPDATE users
                SET 
                    nome = COALESCE(%s, nome),
                    tipo_usuario = COALESCE(%s, tipo_usuario),
                    turma_serie = COALESCE(%s, turma_serie),
                    updated_at = NOW()
                WHERE numero = %s
            """,
                (nome, tipo_usuario, turma_serie, numero),
            )

            conn.commit()
            print(f'🔄 Usuário {numero} atualizado com sucesso')

        except Exception as e:
            print(f'❌ Erro ao atualizar usuário: {e}')

        finally:
            cursor.close()  # ← fechar cursor
            conn.close()

    @staticmethod
    def save_message(session_id: str, message: dict):

        conn = get_vector_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO chat_ia (session_id, message)
                VALUES (%s, %s)
            """,
                (session_id, json.dumps(message)),
            )

            conn.commit()
            print('✅ Mensagem salva com sucesso')

        except Exception as e:
            conn.rollback()
            print(f'❌ Erro ao salvar mensagem no banco: {e}')

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_historico(number: str):
        conn = get_vector_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT message 
                FROM chat_ia
                WHERE session_id = %s
                ORDER BY id ASC
                LIMIT 20
            """,
                (number,),
            )

            rows = cursor.fetchall()
            historico = []

            for row in rows:
                msg = row['message']

                if msg['type'] == 'human':
                    historico.append(HumanMessage(content=msg['content']))

                elif msg['type'] == 'ai':
                    historico.append(AIMessage(content=msg['content']))

                elif msg['type'] == 'tool':
                    historico.append(
                        ToolMessage(
                            content=msg['content'],
                            tool_call_id=msg.get('tool_call_id', ''),
                        )
                    )

            return historico

        except Exception as e:
            print(f'❌ Erro ao recuperar histórico: {e}')
            return []

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_file(categoria: str):

        try:
            conn = get_vector_conn()
            cursor = conn.cursor()

            query = """
                SELECT categoria, fileName, mediaType, caminho
                FROM arquivos
                WHERE categoria ILIKE %s
                LIMIT 1;
            """

            termo = f'%{categoria}%'
            cursor.execute(query, (termo,))

            resultado = cursor.fetchone()
            return resultado

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
