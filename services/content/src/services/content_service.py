"""
Serviço de lógica de negócio para conteúdo (alimentos e exercícios)
"""

from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime

from .firebase_service import FirebaseService
from ..models.food import Food, FoodSearchResponse, NutritionalInfo, ServingSize
from ..models.exercise import (
    Exercise, ExerciseSearchResponse, METValue, 
    MuscleGroup, ExerciseType, Equipment, DifficultyLevel
)

logger = structlog.get_logger()

class ContentService:
    """Serviço para operações de conteúdo"""
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase = firebase_service
        
        # Coleções do Firestore
        self.FOODS_COLLECTION = "foods"
        self.EXERCISES_COLLECTION = "exercises"
        self.MET_VALUES_COLLECTION = "met_values"
    
    async def search_foods(
        self,
        search_term: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> FoodSearchResponse:
        """Buscar alimentos com filtros"""
        try:
            # Preparar filtros do Firestore
            firestore_filters = {}
            
            if filters:
                # Filtro por categoria
                if "category" in filters:
                    firestore_filters["category"] = filters["category"]
                
                # Filtros nutricionais (requerem estrutura específica)
                if "min_protein" in filters:
                    firestore_filters["nutritional_info.protein"] = {">=": filters["min_protein"]}
                
                if "max_calories" in filters:
                    firestore_filters["nutritional_info.calories"] = {"<=": filters["max_calories"]}
            
            # Buscar no Firestore
            result = await self.firebase.search_documents(
                collection=self.FOODS_COLLECTION,
                filters=firestore_filters,
                search_term=search_term,
                search_fields=["name", "tags"] if search_term else None,
                limit=limit,
                offset=offset,
                order_by="name"
            )
            
            # Converter para modelos Pydantic
            foods = []
            for doc in result["documents"]:
                try:
                    food = self._document_to_food(doc)
                    foods.append(food)
                except Exception as e:
                    logger.warning("Erro ao converter documento de alimento", doc_id=doc.get("id"), error=str(e))
                    continue
            
            # Filtrar por busca textual se necessário (fallback)
            if search_term and foods:
                search_lower = search_term.lower()
                foods = [
                    food for food in foods 
                    if search_lower in food.name.lower() or 
                       (food.tags and any(search_lower in tag.lower() for tag in food.tags))
                ]
            
            return FoodSearchResponse(
                foods=foods,
                total=result["total"],
                limit=limit,
                offset=offset,
                has_more=result["has_more"]
            )
            
        except Exception as e:
            logger.error("Erro na busca de alimentos", error=str(e))
            raise
    
    async def get_food_by_id(self, food_id: str) -> Optional[Food]:
        """Obter alimento por ID"""
        try:
            doc = await self.firebase.get_document(self.FOODS_COLLECTION, food_id)
            if doc:
                return self._document_to_food(doc)
            return None
            
        except Exception as e:
            logger.error("Erro ao obter alimento", food_id=food_id, error=str(e))
            raise
    
    async def search_exercises(
        self,
        search_term: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> ExerciseSearchResponse:
        """Buscar exercícios com filtros"""
        try:
            # Preparar filtros do Firestore
            firestore_filters = {}
            
            if filters:
                if "muscle_group" in filters:
                    firestore_filters["primary_muscle_group"] = filters["muscle_group"]
                
                if "equipment" in filters:
                    firestore_filters["equipment"] = {"array_contains": filters["equipment"]}
                
                if "difficulty" in filters:
                    firestore_filters["difficulty"] = filters["difficulty"]
                
                if "exercise_type" in filters:
                    firestore_filters["exercise_type"] = filters["exercise_type"]
            
            # Buscar no Firestore
            result = await self.firebase.search_documents(
                collection=self.EXERCISES_COLLECTION,
                filters=firestore_filters,
                search_term=search_term,
                search_fields=["name", "tags"] if search_term else None,
                limit=limit,
                offset=offset,
                order_by="name"
            )
            
            # Converter para modelos Pydantic
            exercises = []
            for doc in result["documents"]:
                try:
                    exercise = self._document_to_exercise(doc)
                    exercises.append(exercise)
                except Exception as e:
                    logger.warning("Erro ao converter documento de exercício", doc_id=doc.get("id"), error=str(e))
                    continue
            
            # Filtrar por busca textual se necessário (fallback)
            if search_term and exercises:
                search_lower = search_term.lower()
                exercises = [
                    exercise for exercise in exercises 
                    if search_lower in exercise.name.lower() or 
                       (exercise.tags and any(search_lower in tag.lower() for tag in exercise.tags))
                ]
            
            return ExerciseSearchResponse(
                exercises=exercises,
                total=result["total"],
                limit=limit,
                offset=offset,
                has_more=result["has_more"]
            )
            
        except Exception as e:
            logger.error("Erro na busca de exercícios", error=str(e))
            raise
    
    async def get_exercise_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """Obter exercício por ID"""
        try:
            doc = await self.firebase.get_document(self.EXERCISES_COLLECTION, exercise_id)
            if doc:
                return self._document_to_exercise(doc)
            return None
            
        except Exception as e:
            logger.error("Erro ao obter exercício", exercise_id=exercise_id, error=str(e))
            raise
    
    async def get_met_values(self, exercise_type: Optional[str] = None) -> List[METValue]:
        """Obter valores MET para cálculo calórico"""
        try:
            filters = {}
            if exercise_type:
                filters["exercise_type"] = exercise_type
            
            result = await self.firebase.search_documents(
                collection=self.MET_VALUES_COLLECTION,
                filters=filters,
                limit=100,  # MET values são limitados
                order_by="activity"
            )
            
            met_values = []
            for doc in result["documents"]:
                try:
                    met_value = METValue(**doc)
                    met_values.append(met_value)
                except Exception as e:
                    logger.warning("Erro ao converter valor MET", doc_id=doc.get("id"), error=str(e))
                    continue
            
            return met_values
            
        except Exception as e:
            logger.error("Erro ao obter valores MET", error=str(e))
            raise
    
    async def get_food_categories(self) -> List[str]:
        """Obter categorias de alimentos disponíveis"""
        try:
            categories = await self.firebase.get_distinct_values(
                self.FOODS_COLLECTION, 
                "category"
            )
            return sorted(categories)
            
        except Exception as e:
            logger.error("Erro ao obter categorias de alimentos", error=str(e))
            raise
    
    async def get_exercise_categories(self) -> Dict[str, List[str]]:
        """Obter categorias de exercícios disponíveis"""
        try:
            muscle_groups = [group.value for group in MuscleGroup]
            exercise_types = [type_.value for type_ in ExerciseType]
            equipment_list = [eq.value for eq in Equipment]
            difficulties = [diff.value for diff in DifficultyLevel]
            
            return {
                "muscle_groups": muscle_groups,
                "exercise_types": exercise_types,
                "equipment": equipment_list,
                "difficulties": difficulties
            }
            
        except Exception as e:
            logger.error("Erro ao obter categorias de exercícios", error=str(e))
            raise
    
    def _document_to_food(self, doc: Dict[str, Any]) -> Food:
        """Converter documento Firestore para modelo Food"""
        try:
            # Converter nutritional_info
            nutritional_data = doc.get("nutritional_info", {})
            nutritional_info = NutritionalInfo(**nutritional_data)
            
            # Converter serving_sizes
            serving_sizes = []
            for serving_data in doc.get("serving_sizes", []):
                serving_size = ServingSize(**serving_data)
                serving_sizes.append(serving_size)
            
            # Converter timestamps
            created_at = doc.get("created_at")
            updated_at = doc.get("updated_at")
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            return Food(
                id=doc.get("id"),
                name=doc.get("name"),
                name_en=doc.get("name_en"),
                category=doc.get("category"),
                subcategory=doc.get("subcategory"),
                brand=doc.get("brand"),
                barcode=doc.get("barcode"),
                nutritional_info=nutritional_info,
                serving_sizes=serving_sizes,
                description=doc.get("description"),
                ingredients=doc.get("ingredients", []),
                allergens=doc.get("allergens", []),
                tags=doc.get("tags", []),
                source=doc.get("source"),
                verified=doc.get("verified", False),
                created_at=created_at,
                updated_at=updated_at
            )
            
        except Exception as e:
            logger.error("Erro ao converter documento para Food", doc_id=doc.get("id"), error=str(e))
            raise
    
    def _document_to_exercise(self, doc: Dict[str, Any]) -> Exercise:
        """Converter documento Firestore para modelo Exercise"""
        try:
            # Converter timestamps
            created_at = doc.get("created_at")
            updated_at = doc.get("updated_at")
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            return Exercise(
                id=doc.get("id"),
                name=doc.get("name"),
                name_en=doc.get("name_en"),
                primary_muscle_group=doc.get("primary_muscle_group"),
                secondary_muscle_groups=doc.get("secondary_muscle_groups", []),
                exercise_type=doc.get("exercise_type"),
                equipment=doc.get("equipment", []),
                difficulty=doc.get("difficulty"),
                description=doc.get("description"),
                instructions=doc.get("instructions", []),
                premium_guidance=doc.get("premium_guidance"),
                variations=doc.get("variations", []),
                met_value=doc.get("met_value"),
                duration_minutes=doc.get("duration_minutes"),
                tags=doc.get("tags", []),
                video_url=doc.get("video_url"),
                image_urls=doc.get("image_urls", []),
                source=doc.get("source"),
                verified=doc.get("verified", False),
                created_at=created_at,
                updated_at=updated_at
            )
            
        except Exception as e:
            logger.error("Erro ao converter documento para Exercise", doc_id=doc.get("id"), error=str(e))
            raise

