/**
 * Rotas da API para alimentos TBCA
 * EvolveYou Backend - Content Service
 */

const express = require('express');
const { getFoodDatabase } = require('../database/FoodDatabase');

const router = express.Router();

// Middleware para verificar se o banco está carregado
const checkDatabaseReady = (req, res, next) => {
    const db = getFoodDatabase();
    if (!db.isReady()) {
        return res.status(503).json({
            success: false,
            error: 'Database not ready. Please wait for data loading to complete.',
            message: 'Banco de dados não está pronto. Aguarde o carregamento dos dados.'
        });
    }
    next();
};

// GET /api/foods/stats - Estatísticas do banco de dados
router.get('/stats', checkDatabaseReady, (req, res) => {
    try {
        const db = getFoodDatabase();
        const stats = db.getStats();
        
        res.json({
            success: true,
            data: stats
        });
    } catch (error) {
        console.error('Erro ao obter estatísticas:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: 'Erro interno do servidor'
        });
    }
});

// GET /api/foods/groups - Listar grupos de alimentos
router.get('/groups', checkDatabaseReady, (req, res) => {
    try {
        const db = getFoodDatabase();
        const groups = db.getGroups();
        
        res.json({
            success: true,
            data: groups
        });
    } catch (error) {
        console.error('Erro ao obter grupos:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/search - Buscar alimentos por nome
router.get('/search', checkDatabaseReady, (req, res) => {
    try {
        const { q, limit = 20 } = req.query;
        
        if (!q || q.trim().length < 2) {
            return res.status(400).json({
                success: false,
                error: 'Query parameter "q" is required and must have at least 2 characters',
                message: 'Parâmetro de busca "q" é obrigatório e deve ter pelo menos 2 caracteres'
            });
        }
        
        const db = getFoodDatabase();
        const results = db.searchByName(q.trim(), parseInt(limit));
        
        res.json({
            success: true,
            data: results.map(food => food.toJSON()),
            total: results.length,
            query: q.trim()
        });
    } catch (error) {
        console.error('Erro na busca:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/group/:grupo - Buscar alimentos por grupo
router.get('/group/:grupo', checkDatabaseReady, (req, res) => {
    try {
        const { grupo } = req.params;
        const { limit = 50 } = req.query;
        
        const db = getFoodDatabase();
        const results = db.getByGroup(grupo, parseInt(limit));
        
        res.json({
            success: true,
            data: results.map(food => food.toJSON()),
            total: results.length,
            group: grupo
        });
    } catch (error) {
        console.error('Erro ao buscar por grupo:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/:codigo - Buscar alimento específico por código
router.get('/:codigo', checkDatabaseReady, (req, res) => {
    try {
        const { codigo } = req.params;
        
        const db = getFoodDatabase();
        const food = db.getFood(codigo);
        
        if (!food) {
            return res.status(404).json({
                success: false,
                error: 'Food not found',
                message: 'Alimento não encontrado'
            });
        }
        
        res.json({
            success: true,
            data: food.toJSON()
        });
    } catch (error) {
        console.error('Erro ao buscar alimento:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/:codigo/similar - Buscar alimentos similares
router.get('/:codigo/similar', checkDatabaseReady, (req, res) => {
    try {
        const { codigo } = req.params;
        const { limit = 5 } = req.query;
        
        const db = getFoodDatabase();
        const similar = db.findSimilar(codigo, parseInt(limit));
        
        res.json({
            success: true,
            data: similar.map(food => food.toJSON()),
            total: similar.length,
            reference: codigo
        });
    } catch (error) {
        console.error('Erro ao buscar similares:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// POST /api/foods/filter - Filtrar alimentos por critérios nutricionais
router.post('/filter', checkDatabaseReady, (req, res) => {
    try {
        const criteria = req.body;
        const { limit = 50 } = req.query;
        
        const db = getFoodDatabase();
        const results = db.filterByCriteria(criteria, parseInt(limit));
        
        res.json({
            success: true,
            data: results.map(food => food.toJSON()),
            total: results.length,
            criteria: criteria
        });
    } catch (error) {
        console.error('Erro ao filtrar alimentos:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/random/:count - Obter alimentos aleatórios
router.get('/random/:count', checkDatabaseReady, (req, res) => {
    try {
        const { count } = req.params;
        const { grupo } = req.query;
        
        const db = getFoodDatabase();
        const results = db.getRandomFoods(parseInt(count), grupo);
        
        res.json({
            success: true,
            data: results.map(food => food.toJSON()),
            total: results.length,
            count: parseInt(count),
            group: grupo || 'all'
        });
    } catch (error) {
        console.error('Erro ao obter alimentos aleatórios:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/rich/:nutrient - Buscar alimentos ricos em nutriente específico
router.get('/rich/:nutrient', checkDatabaseReady, (req, res) => {
    try {
        const { nutrient } = req.params;
        const { limit = 20 } = req.query;
        
        const db = getFoodDatabase();
        const results = db.getRichInNutrient(nutrient, parseInt(limit));
        
        res.json({
            success: true,
            data: results.map(food => food.toJSON()),
            total: results.length,
            nutrient: nutrient
        });
    } catch (error) {
        console.error('Erro ao buscar alimentos ricos em nutriente:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// GET /api/foods/algorithm/data - Dados formatados para algoritmo de dieta
router.get('/algorithm/data', checkDatabaseReady, (req, res) => {
    try {
        const criteria = req.query;
        
        const db = getFoodDatabase();
        const results = db.getFoodsForDietAlgorithm(criteria);
        
        res.json({
            success: true,
            data: results,
            total: results.length,
            format: 'algorithm'
        });
    } catch (error) {
        console.error('Erro ao obter dados para algoritmo:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// POST /api/foods/import/tbca - Importar dados da TBCA (admin only)
router.post('/import/tbca', async (req, res) => {
    try {
        const { filePath } = req.body;
        
        if (!filePath) {
            return res.status(400).json({
                success: false,
                error: 'File path is required',
                message: 'Caminho do arquivo é obrigatório'
            });
        }
        
        const db = getFoodDatabase();
        const result = await db.importTBCAData(filePath);
        
        res.json({
            success: true,
            message: 'TBCA data imported successfully',
            data: result
        });
    } catch (error) {
        console.error('Erro ao importar dados da TBCA:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to import TBCA data',
            message: error.message
        });
    }
});

// GET /api/foods/health - Health check da API de alimentos
router.get('/health', (req, res) => {
    const db = getFoodDatabase();
    const isReady = db.isReady();
    
    res.status(isReady ? 200 : 503).json({
        success: isReady,
        status: isReady ? 'healthy' : 'not ready',
        database_loaded: isReady,
        foods_count: isReady ? db.foods.size : 0,
        groups_count: isReady ? db.groups.size : 0
    });
});

module.exports = router;

