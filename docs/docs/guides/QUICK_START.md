# 🚀 GUIA DE INÍCIO RÁPIDO - EVOLVEYOU

## ⚡ PARA COMEÇAR IMEDIATAMENTE

### **1. VERIFICAR AMBIENTE**
```bash
# Verificar se repositórios estão atualizados
git clone https://github.com/magnusimports/evolveyou-backend.git
git clone https://github.com/magnusimports/evolveyou-frontend.git

# Testar serviços
cd evolveyou-backend
docker-compose up -d

# Verificar health checks
curl http://localhost:8080/health  # content-service
curl http://localhost:8081/health  # users-service
curl http://localhost:8082/health  # plans-service
```

### **2. PRIORIDADES IMEDIATAS**

#### **🔥 CRÍTICO - Implementar HOJE**
1. **Base de dados TACO** (5% completo)
   - Localização: `evolveyou-backend/services/content-service/`
   - Arquivo: `scripts/populate_taco_database.py`
   - Meta: 3000+ alimentos brasileiros

2. **Telas de anamnese** (20% completo)
   - Localização: `evolveyou-frontend/lib/screens/anamnese/`
   - Meta: 6 telas detalhadas de questionário

3. **Integração frontend-backend** (0% completo)
   - Localização: `evolveyou-frontend/lib/services/`
   - Meta: Conectar todas as APIs

### **3. COMANDOS ESSENCIAIS**

#### **Backend**
```bash
# Iniciar todos os serviços
cd evolveyou-backend
docker-compose up -d

# Popular base de dados
python services/content-service/scripts/populate_database.py

# Executar testes
python -m pytest

# Deploy
gcloud builds submit --config cloudbuild.yaml
```

#### **Frontend**
```bash
# Executar app
cd evolveyou-frontend
flutter run

# Testes
flutter test

# Build para produção
flutter build apk --release
```

### **4. CREDENCIAIS**

#### **GitHub**
- Token: `YOUR_GITHUB_TOKEN`
- Backend: https://github.com/magnusimports/evolveyou-backend
- Frontend: https://github.com/magnusimports/evolveyou-frontend

#### **Google Cloud**
- Project: `evolveyou-prod`
- Console: https://console.cloud.google.com/welcome?project=evolveyou-prod
- Firebase: https://console.firebase.google.com/u/0/?hl=pt-br

### **5. PRÓXIMOS PASSOS (ORDEM)**

1. ✅ **Dia 1-2**: Base de dados TACO completa
2. ✅ **Dia 3-4**: Telas de anamnese detalhadas  
3. ✅ **Dia 5**: Integração frontend-backend
4. ✅ **Dia 6-7**: Sistema de ciclos (Cloud Functions)
5. ✅ **Dia 8-10**: Sistema full-time (rebalanceamento)

### **6. VALIDAÇÃO DE PROGRESSO**

#### **Checklist Diário**
- [ ] Funcionalidade implementada e testada
- [ ] Commit com mensagem clara
- [ ] Documentação atualizada
- [ ] Health checks passando

#### **Marcos Semanais**
- **Semana 1**: Base sólida (dados + anamnese + integração)
- **Semana 2**: Funcionalidades core (ciclos + equivalência)
- **Semana 3**: Sistema full-time completo
- **Semana 4**: Premium + polimento

### **7. CONTATOS DE EMERGÊNCIA**

#### **Recursos Técnicos**
- **Tabela TACO**: https://www.tbca.net.br/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Flutter Docs**: https://flutter.dev/docs
- **Firebase Docs**: https://firebase.google.com/docs

#### **APIs Importantes**
- **Content Service**: http://localhost:8080
- **Users Service**: http://localhost:8081  
- **Plans Service**: http://localhost:8082
- **Tracking Service**: http://localhost:8083

---

## 🆘 SE ALGO DER ERRADO

### **Serviços não iniciam**
```bash
# Limpar containers
docker-compose down -v
docker system prune -f

# Reiniciar
docker-compose up -d --build
```

### **Erro de autenticação**
```bash
# Reconfigurar git
git config --global user.name "Manus Agent"
git config --global user.email "agent@manus.ai"

# Testar token GitHub
curl -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user
```

### **Firebase não conecta**
- Verificar se projeto `evolveyou-prod` está ativo
- Confirmar credenciais no console Firebase
- Testar conexão: `gcloud auth list`

---

**🎯 OBJETIVO**: Entregar aplicativo completo em 20-25 dias
**📅 Data limite**: 09/09/2025
**✅ Status atual**: 65% completo - FALTAM APENAS FUNCIONALIDADES ESPECÍFICAS

**SUCESSO GARANTIDO! 🚀**

