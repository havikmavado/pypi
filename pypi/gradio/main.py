import gradio as gr

# 1. FUNÇÃO: O código Python tradicional
def processar_dados(texto, quantidade):
    return f"Você digitou: '{texto}' | Intensidade: {quantidade}"

# 2. INTERFACE: Onde você usa os componentes do Gradio
demo = gr.Interface(
    fn=processar_dados,
    inputs=[
        gr.Textbox(label="Mensagem", placeholder="Digite algo..."), # Componente de texto
        gr.Slider(minimum=1, maximum=10, value=5, label="Nível")   # Componente de slider
    ],
    outputs=gr.Textbox(label="Resultado"),                        # Componente de saída
    title="Meu Primeiro App"
)

# 3. LANÇAMENTO: Fica sempre no final do arquivo
demo.launch()