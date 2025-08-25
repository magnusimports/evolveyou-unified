#!/usr/bin/env python3
"""
Script para popular o banco de dados Firestore com dados iniciais
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.firebase_service import FirebaseService
from models.food import Food, NutritionalInfo, ServingSize
from models.exercise import Exercise, PremiumGuidance, ExerciseVariation, MuscleGroup, ExerciseType, Equipment, DifficultyLevel
from models.exercise import METValue

class DatabasePopulator:
    """Classe para popular o banco de dados com dados iniciais"""
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        
    async def initialize(self):
        """Inicializar serviços"""
        await self.firebase_service.initialize()
        print("✅ Firebase inicializado com sucesso")
    
    async def load_generated_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Carregar dados gerados do arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Dados carregados de {file_path}")
            return data.get('results', [])
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return []
    
    def parse_food_data(self, content_data: str) -> List[Dict[str, Any]]:
        """Parsear dados de alimentos do JSON string"""
        try:
            foods_data = json.loads(content_data)
            parsed_foods = []
            
            for food_data in foods_data:
                # Converter para formato esperado pelo modelo
                parsed_food = {
                    "name": food_data.get("name", ""),
                    "category": food_data.get("category", ""),
                    "nutritional_info": food_data.get("nutritional_info", {}),
                    "serving_sizes": food_data.get("serving_sizes", []),
                    "description": food_data.get("description", ""),
                    "ingredients": food_data.get("ingredients", []),
                    "allergens": food_data.get("allergens", []),
                    "tags": food_data.get("tags", []),
                    "source": "EvolveYou Initial Data",
                    "verified": True
                }
                parsed_foods.append(parsed_food)
            
            return parsed_foods
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear dados de alimentos: {e}")
            return []
    
    def parse_exercise_data(self, content_data: str) -> List[Dict[str, Any]]:
        """Parsear dados de exercícios do JSON string"""
        try:
            exercises_data = json.loads(content_data)
            parsed_exercises = []
            
            for exercise_data in exercises_data:
                # Converter para formato esperado pelo modelo
                parsed_exercise = {
                    "name": exercise_data.get("name", ""),
                    "primary_muscle_group": exercise_data.get("primary_muscle_group", ""),
                    "secondary_muscle_groups": exercise_data.get("secondary_muscle_groups", []),
                    "exercise_type": exercise_data.get("exercise_type", "forca"),
                    "equipment": exercise_data.get("equipment", []),
                    "difficulty": exercise_data.get("difficulty", "intermediario"),
                    "description": exercise_data.get("description", ""),
                    "instructions": exercise_data.get("instructions", []),
                    "premium_guidance": exercise_data.get("premium_guidance"),
                    "variations": exercise_data.get("variations", []),
                    "met_value": exercise_data.get("met_value"),
                    "duration_minutes": exercise_data.get("duration_minutes"),
                    "tags": exercise_data.get("tags", []),
                    "video_url": exercise_data.get("video_url"),
                    "image_urls": exercise_data.get("image_urls", []),
                    "source": "EvolveYou Initial Data",
                    "verified": True
                }
                parsed_exercises.append(parsed_exercise)
            
            return parsed_exercises
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear dados de exercícios: {e}")
            return []
    
    def parse_met_data(self, content_data: str) -> List[Dict[str, Any]]:
        """Parsear dados de valores MET do JSON string"""
        try:
            met_data = json.loads(content_data)
            parsed_met = []
            
            for met_item in met_data:
                parsed_met_value = {
                    "activity": met_item.get("activity", ""),
                    "met_value": float(met_item.get("met_value", 0)),
                    "exercise_type": met_item.get("exercise_type", ""),
                    "intensity": met_item.get("intensity", ""),
                    "description": met_item.get("description", "")
                }
                parsed_met.append(parsed_met_value)
            
            return parsed_met
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Erro ao parsear dados MET: {e}")
            return []
    
    async def populate_foods(self, foods_data: List[Dict[str, Any]]) -> int:
        """Popular coleção de alimentos"""
        try:
            print(f"📝 Populando {len(foods_data)} alimentos...")
            
            # Criar documentos em lotes
            batch_size = 10
            created_count = 0
            
            for i in range(0, len(foods_data), batch_size):
                batch = foods_data[i:i + batch_size]
                doc_ids = await self.firebase_service.batch_create_documents("foods", batch)
                created_count += len(doc_ids)
                print(f"   ✅ Criados {len(doc_ids)} alimentos (total: {created_count})")
            
            print(f"✅ {created_count} alimentos criados com sucesso")
            return created_count
            
        except Exception as e:
            print(f"❌ Erro ao popular alimentos: {e}")
            return 0
    
    async def populate_exercises(self, exercises_data: List[Dict[str, Any]]) -> int:
        """Popular coleção de exercícios"""
        try:
            print(f"💪 Populando {len(exercises_data)} exercícios...")
            
            # Criar documentos em lotes
            batch_size = 10
            created_count = 0
            
            for i in range(0, len(exercises_data), batch_size):
                batch = exercises_data[i:i + batch_size]
                doc_ids = await self.firebase_service.batch_create_documents("exercises", batch)
                created_count += len(doc_ids)
                print(f"   ✅ Criados {len(doc_ids)} exercícios (total: {created_count})")
            
            print(f"✅ {created_count} exercícios criados com sucesso")
            return created_count
            
        except Exception as e:
            print(f"❌ Erro ao popular exercícios: {e}")
            return 0
    
    async def populate_met_values(self, met_data: List[Dict[str, Any]]) -> int:
        """Popular coleção de valores MET"""
        try:
            print(f"⚡ Populando {len(met_data)} valores MET...")
            
            doc_ids = await self.firebase_service.batch_create_documents("met_values", met_data)
            
            print(f"✅ {len(doc_ids)} valores MET criados com sucesso")
            return len(doc_ids)
            
        except Exception as e:
            print(f"❌ Erro ao popular valores MET: {e}")
            return 0
    
    async def populate_all(self, data_file: str):
        """Popular todas as coleções com dados do arquivo"""
        print("🚀 Iniciando população do banco de dados...")
        
        # Carregar dados gerados
        generated_data = await self.load_generated_data(data_file)
        
        if not generated_data:
            print("❌ Nenhum dado encontrado para popular")
            return
        
        # Contadores
        total_foods = 0
        total_exercises = 0
        total_met_values = 0
        
        # Processar cada resultado
        for result in generated_data:
            output = result.get('output', {})
            category = output.get('category', '')
            content_data = output.get('content_data', '')
            
            if not content_data:
                continue
            
            try:
                if category == 'alimentos':
                    foods = self.parse_food_data(content_data)
                    if foods:
                        count = await self.populate_foods(foods)
                        total_foods += count
                
                elif category == 'exercícios':
                    exercises = self.parse_exercise_data(content_data)
                    if exercises:
                        count = await self.populate_exercises(exercises)
                        total_exercises += count
                
                elif category == 'met_values':
                    met_values = self.parse_met_data(content_data)
                    if met_values:
                        count = await self.populate_met_values(met_values)
                        total_met_values += count
                        
            except Exception as e:
                print(f"❌ Erro ao processar categoria {category}: {e}")
                continue
        
        # Resumo final
        print("\n" + "="*50)
        print("📊 RESUMO DA POPULAÇÃO DO BANCO")
        print("="*50)
        print(f"🍎 Alimentos criados: {total_foods}")
        print(f"💪 Exercícios criados: {total_exercises}")
        print(f"⚡ Valores MET criados: {total_met_values}")
        print(f"📈 Total de documentos: {total_foods + total_exercises + total_met_values}")
        print("="*50)
        print("✅ População do banco concluída com sucesso!")

async def main():
    """Função principal"""
    # Verificar se arquivo de dados existe
    data_file = "/home/ubuntu/create_initial_content_data.json"
    
    if not os.path.exists(data_file):
        print(f"❌ Arquivo de dados não encontrado: {data_file}")
        return
    
    # Criar e executar populador
    populator = DatabasePopulator()
    
    try:
        await populator.initialize()
        await populator.populate_all(data_file)
        
    except Exception as e:
        print(f"❌ Erro durante a população: {e}")
        
    finally:
        print("🏁 Script finalizado")

if __name__ == "__main__":
    asyncio.run(main())

