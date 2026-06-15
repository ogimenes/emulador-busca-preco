import flet as ft
import socket
import time

def main(page: ft.Page):
    # Configurações da Janela/App
    page.title = "Busca Preço"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f172a"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Elementos Visuais
    txt_desc = ft.Text("Passe o código de barras", size=22, color="#94a3b8", text_align=ft.TextAlign.CENTER)
    txt_preco = ft.Text("---", size=55, weight=ft.FontWeight.BOLD, color="#10b981")
    
    # Campo de entrada (invisível ou visível, dependendo do hardware)
    input_codigo = ft.TextField(
        label="EAN", 
        autofocus=True, 
        width=300, 
        text_align=ft.TextAlign.CENTER,
        border_color="#3b82f6"
    )

    # Lógica de Consulta (Equivalente ao Add_KeyDown do PowerShell)
    def consultar(e):
        codigo = input_codigo.value.strip()
        if not codigo: return

        # Atualiza a UI para estado de carregamento
        txt_desc.value = "A CONSULTAR..."
        txt_preco.value = "---"
        txt_preco.color = "#3b82f6"
        page.update()

        try:
            # Conexão TCP idêntica ao emulador
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.5) # Timeout para não travar o app
            client.connect(("192.168.127.5", 6500))
            
            # Handshake e envio
            client.sendall(b"#ID|01#")
            time.sleep(0.4) 
            client.sendall(f"#{codigo}#".encode("utf-8"))
            
            # Leitura da resposta
            res = client.recv(1024).decode("utf-8")
            
            if "|" in res:
                # Tratamento da string recebida
                partes = [p for p in res.split('#') if p.strip()]
                util = next((p for p in partes if "|" in p), None)
                
                if util:
                    dados = util.split('|')
                    txt_desc.value = dados[0].strip().upper()
                    txt_preco.value = dados[-1].strip()
                    txt_preco.color = "#10b981" # Fica verde
            else:
                txt_desc.value = "PRODUTO NÃO ENCONTRADO"
                txt_preco.color = "#ef4444" # Fica vermelho

        except Exception as ex:
            txt_desc.value = "OFFLINE / ERRO DE REDE"
            txt_preco.color = "#ef4444"
        
        finally:
            client.close()
            input_codigo.value = ""
            input_codigo.focus() # Retorna o foco para o próximo bip
            page.update()

    # Dispara a função 'consultar' ao apertar Enter
    input_codigo.on_submit = consultar

    # Adiciona tudo na tela
    page.add(txt_desc, txt_preco, ft.Container(height=40), input_codigo)

# Roda o aplicativo
ft.app(target=main)
