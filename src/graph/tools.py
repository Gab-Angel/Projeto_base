from langchain.tools import tool
from langgraph.prebuilt import ToolNode

from src.agent.base_agent import llm_groq


class Tools:
    @tool(
        description=""""
        Essa tool retorna 'Agente com tools funcionando'
        """
    )
    def tool_funcionando():

        return 'Agente com tools funcionando'

    tools = [tool_funcionando]
    tool_node = ToolNode(tools)
    llm_with_tools = llm_groq.bind_tools(tools)
