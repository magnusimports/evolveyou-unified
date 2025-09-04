from flask import Blueprint, request, jsonify
import secrets
import json
from datetime import datetime

evolveyou_bp = Blueprint('evolveyou', __name__)

# Dados mock para demonstração
mock_users = {}
mock_workouts = []
mock_meals = []
mock_weight = []

@evolveyou_bp.route('/auth/register', methods=['POST'])
def register():
    """Registrar novo usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user_id = len(mock_users) + 1
        token = 'demo_token_' + secrets.token_hex(16)
        
        user = {
            'id': user_id,
            'name': data.get('name', 'Usuário'),
            'email': data.get('email'),
            'onboarding_completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        mock_users[user_id] = user
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'access_token': token,
            'user': user
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evolveyou_bp.route('/auth/login', methods=['POST'])
def login():
    """Fazer login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        token = 'demo_token_' + secrets.token_hex(16)
        
        user = {
            'id': 1,
            'name': 'João Silva',
            'email': data.get('email'),
            'onboarding_completed': True
        }
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': token,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evolveyou_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """Obter usuário atual"""
    return jsonify({
        'id': 1,
        'name': 'João Silva',
        'email': 'joao@evolveyou.com',
        'onboarding_completed': True
    }), 200

@evolveyou_bp.route('/auth/onboarding', methods=['POST'])
def complete_onboarding():
    """Completar onboarding"""
    try:
        data = request.get_json()
        
        return jsonify({
            'message': 'Onboarding completado com sucesso',
            'user': {
                'id': 1,
                'name': 'João Silva',
                'email': 'joao@evolveyou.com',
                'onboarding_completed': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evolveyou_bp.route('/content/exercises', methods=['GET'])
def get_exercises():
    """Obter exercícios"""
    exercises = [
        {
            'id': 1,
            'name': 'Supino Reto',
            'muscle_group': 'Peito',
            'difficulty': 'Intermediário',
            'equipment': 'Barra',
            'instructions': 'Deite no banco e empurre a barra para cima'
        },
        {
            'id': 2,
            'name': 'Agachamento',
            'muscle_group': 'Pernas',
            'difficulty': 'Iniciante',
            'equipment': 'Peso corporal',
            'instructions': 'Desça como se fosse sentar em uma cadeira'
        }
    ]
    
    return jsonify({'exercises': exercises}), 200

@evolveyou_bp.route('/content/recipes', methods=['GET'])
def get_recipes():
    """Obter receitas"""
    recipes = [
        {
            'id': 1,
            'name': 'Frango Grelhado',
            'meal_type': 'Almoço',
            'calories': 250,
            'protein': 30,
            'carbs': 0,
            'fat': 12,
            'ingredients': ['Peito de frango', 'Temperos'],
            'instructions': 'Grelhe o frango até dourar'
        },
        {
            'id': 2,
            'name': 'Aveia com Banana',
            'meal_type': 'Café da manhã',
            'calories': 180,
            'protein': 6,
            'carbs': 35,
            'fat': 3,
            'ingredients': ['Aveia', 'Banana', 'Leite'],
            'instructions': 'Misture tudo e aqueça'
        }
    ]
    
    return jsonify({'recipes': recipes}), 200

@evolveyou_bp.route('/plans/workout', methods=['GET'])
def get_workout_plan():
    """Obter plano de treino"""
    plan = {
        'week': [
            {
                'day': 'Segunda',
                'focus': 'Peito e Tríceps',
                'exercises': [
                    {'name': 'Supino Reto', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Supino Inclinado', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Tríceps Pulley', 'sets': 3, 'reps': '10-15'}
                ]
            },
            {
                'day': 'Terça',
                'focus': 'Costas e Bíceps',
                'exercises': [
                    {'name': 'Puxada Frontal', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Remada Curvada', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Rosca Direta', 'sets': 3, 'reps': '10-15'}
                ]
            }
        ]
    }
    
    return jsonify(plan), 200

@evolveyou_bp.route('/plans/diet', methods=['GET'])
def get_diet_plan():
    """Obter plano de dieta"""
    plan = {
        'daily_calories': 2000,
        'macros': {
            'protein': 150,
            'carbs': 200,
            'fat': 67
        },
        'meals': [
            {
                'meal': 'Café da manhã',
                'time': '07:00',
                'foods': ['Aveia com banana', 'Café com leite'],
                'calories': 400
            },
            {
                'meal': 'Almoço',
                'time': '12:00',
                'foods': ['Frango grelhado', 'Arroz integral', 'Salada'],
                'calories': 600
            },
            {
                'meal': 'Jantar',
                'time': '19:00',
                'foods': ['Peixe assado', 'Batata doce', 'Legumes'],
                'calories': 500
            }
        ]
    }
    
    return jsonify(plan), 200

@evolveyou_bp.route('/tracking/workouts', methods=['POST'])
def log_workout():
    """Registrar treino"""
    try:
        data = request.get_json()
        
        workout = {
            'id': len(mock_workouts) + 1,
            'date': datetime.now().isoformat(),
            'exercises': data.get('exercises', []),
            'duration': data.get('duration', 60),
            'notes': data.get('notes', '')
        }
        
        mock_workouts.append(workout)
        
        return jsonify({
            'message': 'Treino registrado com sucesso',
            'workout': workout
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evolveyou_bp.route('/tracking/workouts', methods=['GET'])
def get_workout_history():
    """Obter histórico de treinos"""
    return jsonify({'workouts': mock_workouts}), 200

@evolveyou_bp.route('/tracking/weight', methods=['POST'])
def log_weight():
    """Registrar peso"""
    try:
        data = request.get_json()
        
        weight_entry = {
            'id': len(mock_weight) + 1,
            'weight': data.get('weight'),
            'date': datetime.now().isoformat()
        }
        
        mock_weight.append(weight_entry)
        
        return jsonify({
            'message': 'Peso registrado com sucesso',
            'entry': weight_entry
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evolveyou_bp.route('/tracking/weight', methods=['GET'])
def get_weight_history():
    """Obter histórico de peso"""
    return jsonify({'weights': mock_weight}), 200

@evolveyou_bp.route('/tracking/dashboard', methods=['GET'])
def get_dashboard():
    """Obter dados do dashboard"""
    stats = {
        'total_workouts': len(mock_workouts),
        'current_weight': mock_weight[-1]['weight'] if mock_weight else 70,
        'calories_today': 1800,
        'weekly_goal': 4,
        'workouts_this_week': 3,
        'recent_workouts': mock_workouts[-5:] if mock_workouts else [],
        'weight_trend': mock_weight[-7:] if mock_weight else []
    }
    
    return jsonify(stats), 200

# Rotas para funcionalidades de progresso
@evolveyou_bp.route('/tracking/measurements', methods=['GET'])
def get_measurements():
    """Obter medidas corporais"""
    measurements = [
        {
            'date': '2025-09-01',
            'chest': 100,
            'waist': 85,
            'hips': 95,
            'bicep': 35,
            'thigh': 60
        }
    ]
    return jsonify({'measurements': measurements}), 200

@evolveyou_bp.route('/tracking/measurements', methods=['POST'])
def log_measurements():
    """Registrar medidas corporais"""
    data = request.get_json()
    return jsonify({'message': 'Medidas registradas com sucesso'}), 201

@evolveyou_bp.route('/tracking/photos', methods=['GET'])
def get_progress_photos():
    """Obter fotos de progresso"""
    photos = []
    return jsonify({'photos': photos}), 200

@evolveyou_bp.route('/tracking/photos', methods=['POST'])
def upload_progress_photo():
    """Upload de foto de progresso"""
    return jsonify({'message': 'Foto enviada com sucesso'}), 201

@evolveyou_bp.route('/tracking/achievements', methods=['GET'])
def get_achievements():
    """Obter conquistas"""
    achievements = [
        {
            'title': 'Primeira Semana',
            'description': 'Complete sua primeira semana de treinos',
            'date': '2025-09-01'
        }
    ]
    return jsonify({'achievements': achievements}), 200

@evolveyou_bp.route('/tracking/goals', methods=['GET'])
def get_goals():
    """Obter metas"""
    goals = [
        {
            'title': 'Perder 5kg',
            'progress': 60,
            'target_date': '2025-12-31'
        }
    ]
    return jsonify({'goals': goals}), 200

