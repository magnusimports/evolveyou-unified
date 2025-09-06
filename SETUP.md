# 🔧 Guia de Configuração - EvolveYou

## 🔐 Configuração do Firebase

### 1. Obter Credenciais do Firebase

1. Acesse o [Firebase Console](https://console.firebase.google.com/)
2. Selecione o projeto `evolveyou-prod`
3. Vá em **Configurações do Projeto** > **Contas de Serviço**
4. Clique em **Gerar nova chave privada**
5. Baixe o arquivo JSON

### 2. Configurar Credenciais

1. Renomeie o arquivo baixado para `serviceAccountKey.json`
2. Coloque na raiz do projeto
3. Configure a variável de ambiente:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json
   ```

## 🚀 Executar o Projeto

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

### Backend
```bash
cd services/users
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=../../serviceAccountKey.json
export FIREBASE_PROJECT_ID=evolveyou-prod
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

## 🔒 Segurança

⚠️ **IMPORTANTE:** 
- Nunca faça commit do arquivo `serviceAccountKey.json`
- Use variáveis de ambiente para credenciais

