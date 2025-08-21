from typing import Any

import gradio as gr

"""
Este script é responsável pela geração e utilização do Gradio como interface gráfica para o agente
"""

def gradio_interface_run(agent_talk) -> Any:
    """
    Função responsável por realizar a criação da interface utilizando gradio

    :param agent_talk:
    :return: Any
    """
    iface = gr.ChatInterface(
        fn=agent_talk,
        title="IA AGENT Especialista na REN 1000",
        description="Faça perguntas sobre a REN 1000 da ANEEL",
        type='messages',
        chatbot=gr.Chatbot(height=400,type="messages")
    )

    iface.launch(share=True)