/**
 * Servidor Node.js para APIs de alimentos TBCA
 * EvolveYou Backend - Content Service
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const { getFoodDatabase } = require('./database/FoodDatabase');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Importar rotas
const foodsRouter = require('./routes/foods');

// Usar rotas
app.use('/api/foods', foodsRouter);

// Rota raiz
app.get('/', (req, res) => {
    res.json({
        service: 'EvolveYou Content Service - Foods API',
        version: '1.0.0',
        status: 'running',
        endpoints: {
            foods: '/api/foods',
            health: '/api/foods/health',
            stats: '/api/foods/stats',
            search: '/api/foods/search?q=arroz',
            groups: '/api/foods/groups'
        }
    });
});

// Health check
app.get('/health', (req, res) => {
    const db = getFoodDatabase();
    const isReady = db.isReady();
    
    res.status(isReady ? 200 : 503).json({
        status: isReady ? 'healthy' : 'not ready',
        service: 'content-service-foods-api',
        database_loaded: isReady,
        foods_count: isReady ? db.foods.size : 0,
        groups_count: isReady ? db.groups.size : 0,
        timestamp: new Date().toISOString()
    });
});

// Error handler
app.use((error, req, res, next) => {
    console.error('Erro não tratado:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: error.message
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        message: `Endpoint ${req.method} ${req.originalUrl} não encontrado`
    });
});

// Função para inicializar o banco de dados
async function initializeDatabase() {
    try {
        console.log('🔄 Inicializando banco de dados de alimentos...');
        
        const db = getFoodDatabase();
        
        // Tentar carregar dados existentes
        try {
            await db.loadData();
            console.log('✅ Dados existentes carregados com sucesso');
        } catch (error) {
            console.log('⚠️  Dados não encontrados, tentando importar da TBCA...');
            
            // Tentar importar dados da TBCA
            const tbcaFile = path.join(__dirname, '../tbca_amostra.json');
            try {
                await db.importTBCAData(tbcaFile);
                console.log('✅ Dados da TBCA importados com sucesso');
            } catch (importError) {
                console.error('❌ Erro ao importar dados da TBCA:', importError.message);
                console.log('⚠️  Servidor iniciará sem dados de alimentos');
            }
        }
        
        if (db.isReady()) {
            const stats = db.getStats();
            console.log('📊 Estatísticas do banco:');
            console.log(`   - Total de alimentos: ${stats.total_foods}`);
            console.log(`   - Grupos: ${stats.groups}`);
            console.log(`   - Grupos disponíveis: ${stats.groups_list.join(', ')}`);
        }
        
    } catch (error) {
        console.error('❌ Erro ao inicializar banco de dados:', error);
    }
}

// Iniciar servidor
async function startServer() {
    try {
        // Inicializar banco de dados
        await initializeDatabase();
        
        // Iniciar servidor HTTP
        app.listen(PORT, '0.0.0.0', () => {
            console.log('🚀 EvolveYou Content Service - Foods API');
            console.log('=' * 50);
            console.log(`✅ Servidor rodando em: http://0.0.0.0:${PORT}`);
            console.log(`📊 Health check: http://0.0.0.0:${PORT}/health`);
            console.log(`🔍 API Foods: http://0.0.0.0:${PORT}/api/foods`);
            console.log(`📈 Estatísticas: http://0.0.0.0:${PORT}/api/foods/stats`);
            console.log('=' * 50);
        });
        
    } catch (error) {
        console.error('❌ Erro ao iniciar servidor:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🔄 Recebido SIGTERM, finalizando servidor...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('🔄 Recebido SIGINT, finalizando servidor...');
    process.exit(0);
});

// Iniciar aplicação
if (require.main === module) {
    startServer();
}

module.exports = app;

