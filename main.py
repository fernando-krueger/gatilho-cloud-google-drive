import os
from flask import Flask
from googleapiclient.discovery import build
import google.auth
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
# O ID é a parte final da URL da sua pasta no navegador:
# Ex: drive.google.com/drive/folders/1abc123456789...
ID_PASTA_ALVO = "1waITuhNjMHuTlN_Aafwxhf9312ra8TST"

@app.route("/", methods=["POST", "GET"])
def verificar_e_renomear():
    try:
        # 1. Autenticação Automática no Google Cloud
        creds, _ = google.auth.default()
        service = build('drive', 'v3', credentials=creds)
        
        # 2. Query para buscar pastas DENTRO da pasta específica
        # 'q' filtra por: pai é o ID alvo, é uma pasta e não está na lixeira
        query = f"'{ID_PASTA_ALVO}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        
        resultado = service.files().list(
            q=query, 
            fields="files(id, name)"
        ).execute()
        
        pastas = resultado.get('files', [])

        for pasta in pastas:
            nome_atual = pasta['name']
            
            # 3. Lógica para não renomear o que já foi lido
            if "(lido as" not in nome_atual:
                agora = datetime.now().strftime("%H:%M")
                novo_nome = f"{nome_atual} (lido as {agora})"
                
                # Executa o renomeio no Drive
                service.files().update(
                    fileId=pasta['id'], 
                    body={'name': novo_nome}
                ).execute()
                print(f"Sucesso: {nome_atual} -> {novo_nome}")

        return f"Processado {len(pastas)} pastas.", 200

    except Exception as e:
        print(f"Erro detalhado: {e}")
        return f"Erro: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))