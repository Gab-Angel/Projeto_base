from langgraph.graph import END, StateGraph

from src.graph.nodes import Nodes
from src.graph.state import State

workflow = StateGraph(State)


workflow.add_node('verifyr_user', lambda state: state)
workflow.add_node('save_user', Nodes.node_save_user)
workflow.add_node('save_msg_human', Nodes.node_save_message_human)
workflow.add_node('sender_message', Nodes.node_sender_message)
workflow.add_node('save_msg_ai', Nodes.node_save_message_ai)
workflow.add_node('agente_ai', Nodes.node_agente_assistente)
workflow.add_node('use_tools', Nodes.node_use_tools)
workflow.add_node('execute_tools', Nodes.node_execute_tools)


workflow.set_entry_point('verifyr_user')

workflow.add_conditional_edges(
    'verifyr_user',
    Nodes.node_verify_user,
    {'new': 'save_user', 'existent': 'save_msg_human'},
)

workflow.add_edge('save_user', 'save_msg_human')
workflow.add_edge('save_msg_human', 'agente_ai')

workflow.add_conditional_edges(
    'agente_ai',
    Nodes.node_use_tools,
    {'yes': 'execute_tools', 'no': 'sender_message'},
)

workflow.add_edge('execute_tools', 'agente_ai')
workflow.add_edge('sender_message', 'save_msg_ai')
workflow.add_edge('save_msg_ai', END)


graph = workflow.compile()
