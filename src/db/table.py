import time

from src.db.conection import get_vector_conn


def create_tables(retries=10, delay=3):
    for attempt in range(1, retries + 1):
        try:
            conn = get_vector_conn()
            cursor = conn.cursor()

            sql = """
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE EXTENSION IF NOT EXISTS pgcrypto;

            CREATE TABLE IF NOT EXISTS users (
                numero VARCHAR(20) PRIMARY KEY,
                nome VARCHAR(200),
                tipo_usuario VARCHAR(20),
                turma_serie VARCHAR(50),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo'),
                updated_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo')
            );

            CREATE TABLE IF NOT EXISTS chat_ia (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(20),
                message JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo')
            );

            CREATE TABLE IF NOT EXISTS rag_embeddings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                categoria VARCHAR(100),
                embedding VECTOR(768),
                created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo')
            );

            CREATE INDEX IF NOT EXISTS rag_embedding_idx
            ON rag_embeddings
            USING hnsw (embedding vector_cosine_ops);

            CREATE INDEX IF NOT EXISTS rag_categoria_idx
            ON rag_embeddings (categoria);

            CREATE TABLE IF NOT EXISTS arquivos (
                id SERIAL PRIMARY KEY,
                categoria VARCHAR(100) NOT NULL,
                fileName VARCHAR(255) NOT NULL,
                mediaType VARCHAR(20) NOT NULL,
                caminho VARCHAR NOT NULL,
                criado_em TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo')
            );

            CREATE INDEX IF NOT EXISTS arquivos_categoria_idx
            ON arquivos (categoria);

            CREATE INDEX IF NOT EXISTS arquivos_mediaType_idx
            ON arquivos (mediaType);

            CREATE INDEX IF NOT EXISTS arquivos_fileName_idx
            ON arquivos (fileName);
            """

            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()

            print('✅ Banco inicializado com sucesso!')
            return

        except Exception as e:
            print(
                f'⏳ Banco não disponível (tentativa {attempt}/{retries}): {e}'
            )
            time.sleep(delay)

    raise RuntimeError(
        '❌ Não foi possível conectar ao banco após várias tentativas'
    )


def clean_tables():
    conn = get_vector_conn()
    cursor = conn.cursor()

    try:
        cursor.execute('TRUNCATE TABLE chat_ia RESTART IDENTITY')
        cursor.execute('TRUNCATE TABLE users CASCADE')
        # cursor.execute("TRUNCATE TABLE rag_embeddings RESTART IDENTITY")  # ← adicionar
        conn.commit()
        print('✅ Tabelas limpas com sucesso!')

    except Exception as e:
        conn.rollback()  # ← boa prática adicionar rollback
        print(f'❌ Erro ao limpar tabelas: {e}')

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    confirmacao = input(
        '⚠️  Tem certeza que deseja limpar TODAS as tabelas? (sim/não): '
    )

    if confirmacao.lower() == 'sim':
        clean_tables()
    else:
        print('❌ Operação cancelada.')
