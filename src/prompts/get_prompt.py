import os


def get_prompt(prompt_name: str) -> str:

    base_path = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_path, f'{prompt_name}.txt')

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Prompt '{prompt_name}.txt' não encontrado em {base_path}"
        )

    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()
