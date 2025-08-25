"""
Adaptador de Dados da Base TACO
Converte dados da Base TACO para formato esperado pelo algoritmo de dieta
"""

import logging
from typing import List, Dict, Optional, Any
import structlog

logger = structlog.get_logger(__name__)

class TacoDataAdapter:
    """Adaptador para converter dados da Base TACO para formato do Plans-Service"""
    
    def __init__(self):
        """Inicializa o adaptador com mapeamentos de conversão"""
        self.category_mapping = {
            "CEREAIS E DERIVADOS": "cereais",
            "CARNES E DERIVADOS": "proteinas",
            "FRUTAS E DERIVADOS": "frutas",
            "VERDURAS E LEGUMES": "vegetais",
            "LEGUMINOSAS": "leguminosas",
            "OLEAGINOSAS": "oleaginosas",
            "LATICÍNIOS": "laticinios",
            "AÇÚCARES E DOCES": "doces",
            "ÓLEOS E GORDURAS": "gorduras",
            "BEBIDAS": "bebidas"
        }
        
        self.cost_level_mapping = {
            "CEREAIS E DERIVADOS": "low",
            "CARNES E DERIVADOS": "high", 
            "FRUTAS E DERIVADOS": "medium",
            "VERDURAS E LEGUMES": "low",
            "LEGUMINOSAS": "low",
            "OLEAGINOSAS": "high",
            "LATICÍNIOS": "medium",
            "AÇÚCARES E DOCES": "medium",
            "ÓLEOS E GORDURAS": "medium",
            "BEBIDAS": "medium"
        }
        
    def convert_foods_from_taco(self, taco_foods: List[Dict]) -> List[Dict]:
        """
        Converte lista de alimentos da Base TACO para formato do Plans-Service
        
        Args:
            taco_foods: Lista de alimentos no formato da Base TACO
            
        Returns:
            List[Dict]: Lista de alimentos no formato esperado pelo algoritmo
        """
        try:
            converted_foods = []
            
            for taco_food in taco_foods:
                converted_food = self._convert_single_food(taco_food)
                if converted_food:
                    converted_foods.append(converted_food)
            
            logger.info("Alimentos convertidos com sucesso", 
                       original_count=len(taco_foods),
                       converted_count=len(converted_foods))
            
            return converted_foods
            
        except Exception as e:
            logger.error("Erro ao converter alimentos da TACO", error=str(e))
            return []
    
    def _convert_single_food(self, taco_food: Dict) -> Optional[Dict]:
        """
        Converte um único alimento da Base TACO
        
        Args:
            taco_food: Alimento no formato da Base TACO
            
        Returns:
            Dict: Alimento convertido ou None se inválido
        """
        try:
            # Extrair dados básicos
            food_id = taco_food.get("codigo", "")
            name = taco_food.get("nome", "")
            group = taco_food.get("grupo", "")
            composition = taco_food.get("composicao", {})
            
            if not food_id or not name or not composition:
                logger.warning("Alimento incompleto ignorado", food_id=food_id, name=name)
                return None
            
            # Extrair valores nutricionais
            nutrition = self._extract_nutrition(composition)
            if not nutrition:
                logger.warning("Dados nutricionais inválidos", food_id=food_id)
                return None
            
            # Converter categoria
            category = self.category_mapping.get(group, "outros")
            
            # Estimar tempo de preparo baseado na categoria
            preparation_time = self._estimate_preparation_time(category, name)
            
            # Estimar nível de custo baseado no grupo
            cost_level = self.cost_level_mapping.get(group, "medium")
            
            # Calcular score de disponibilidade (frutas e vegetais sazonais)
            availability_score = self._calculate_availability_score(category, name)
            
            # Determinar tags dietéticas
            dietary_tags = self._determine_dietary_tags(category, name)
            
            # Determinar alergênicos
            allergens = self._determine_allergens(name, group)
            
            converted_food = {
                "id": food_id,
                "name": name,
                "nutrition": nutrition,
                "category": category,
                "preparation_time": preparation_time,
                "cost_level": cost_level,
                "availability_score": availability_score,
                "dietary_tags": dietary_tags,
                "allergens": allergens,
                "source": "TACO",
                "original_group": group
            }
            
            return converted_food
            
        except Exception as e:
            logger.error("Erro ao converter alimento individual", 
                        food_id=taco_food.get("codigo", "unknown"),
                        error=str(e))
            return None
    
    def _extract_nutrition(self, composition: Dict) -> Optional[Dict]:
        """
        Extrai valores nutricionais da composição TACO
        
        Args:
            composition: Dados de composição da TACO
            
        Returns:
            Dict: Valores nutricionais padronizados
        """
        try:
            # Extrair valores principais (por 100g)
            calories = self._get_nutrient_value(composition, "Energia", 0)
            protein = self._get_nutrient_value(composition, "Proteína", 0)
            carbs = self._get_nutrient_value(composition, "Carboidrato total", 0)
            fat = self._get_nutrient_value(composition, "Lipídios", 0)
            fiber = self._get_nutrient_value(composition, "Fibra alimentar", 0)
            
            # Validar valores mínimos
            if calories <= 0:
                return None
            
            nutrition = {
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "fiber": fiber,
                
                # Micronutrientes importantes
                "calcium": self._get_nutrient_value(composition, "Cálcio", 0),
                "iron": self._get_nutrient_value(composition, "Ferro", 0),
                "sodium": self._get_nutrient_value(composition, "Sódio", 0),
                "potassium": self._get_nutrient_value(composition, "Potássio", 0),
                "vitamin_c": self._get_nutrient_value(composition, "Vitamina C", 0),
                
                # Dados calculados
                "calories_per_gram": calories / 100,
                "protein_percentage": (protein * 4 / calories * 100) if calories > 0 else 0,
                "carbs_percentage": (carbs * 4 / calories * 100) if calories > 0 else 0,
                "fat_percentage": (fat * 9 / calories * 100) if calories > 0 else 0
            }
            
            return nutrition
            
        except Exception as e:
            logger.error("Erro ao extrair nutrição", error=str(e))
            return None
    
    def _get_nutrient_value(self, composition: Dict, nutrient_name: str, default: float) -> float:
        """
        Extrai valor de um nutriente específico
        
        Args:
            composition: Dados de composição
            nutrient_name: Nome do nutriente
            default: Valor padrão se não encontrado
            
        Returns:
            float: Valor do nutriente
        """
        try:
            nutrient_data = composition.get(nutrient_name, {})
            if isinstance(nutrient_data, dict):
                value = nutrient_data.get("valor", default)
                return float(value) if value is not None else default
            return default
        except (ValueError, TypeError):
            return default
    
    def _estimate_preparation_time(self, category: str, name: str) -> int:
        """
        Estima tempo de preparo baseado na categoria e nome
        
        Args:
            category: Categoria do alimento
            name: Nome do alimento
            
        Returns:
            int: Tempo estimado em minutos
        """
        name_lower = name.lower()
        
        # Alimentos que não precisam preparo
        if any(word in name_lower for word in ["in natura", "fresco", "cru"]):
            return 0
        
        # Por categoria
        category_times = {
            "frutas": 5,
            "vegetais": 15,
            "cereais": 20,
            "proteinas": 25,
            "leguminosas": 30,
            "oleaginosas": 5,
            "laticinios": 5,
            "doces": 10,
            "gorduras": 2,
            "bebidas": 2
        }
        
        return category_times.get(category, 15)
    
    def _calculate_availability_score(self, category: str, name: str) -> float:
        """
        Calcula score de disponibilidade do alimento
        
        Args:
            category: Categoria do alimento
            name: Nome do alimento
            
        Returns:
            float: Score de 0.0 a 1.0
        """
        # Alimentos básicos têm alta disponibilidade
        if category in ["cereais", "leguminosas", "oleaginosas"]:
            return 0.95
        
        # Frutas e vegetais podem ser sazonais
        if category in ["frutas", "vegetais"]:
            return 0.80
        
        # Proteínas e laticínios geralmente disponíveis
        if category in ["proteinas", "laticinios"]:
            return 0.85
        
        return 0.75
    
    def _determine_dietary_tags(self, category: str, name: str) -> List[str]:
        """
        Determina tags dietéticas do alimento
        
        Args:
            category: Categoria do alimento
            name: Nome do alimento
            
        Returns:
            List[str]: Lista de tags dietéticas
        """
        tags = []
        name_lower = name.lower()
        
        # Tags por categoria
        if category == "proteinas":
            if any(word in name_lower for word in ["carne", "boi", "porco", "frango", "peixe"]):
                tags.append("meat")
        
        if category == "laticinios":
            tags.extend(["dairy", "lactose"])
        
        if category in ["frutas", "vegetais", "cereais", "leguminosas", "oleaginosas"]:
            tags.append("vegetarian")
            tags.append("vegan")
        
        # Glúten (cereais específicos)
        if category == "cereais":
            if any(word in name_lower for word in ["trigo", "aveia", "cevada", "centeio"]):
                tags.append("gluten")
        
        return tags
    
    def _determine_allergens(self, name: str, group: str) -> List[str]:
        """
        Determina alergênicos do alimento
        
        Args:
            name: Nome do alimento
            group: Grupo do alimento
            
        Returns:
            List[str]: Lista de alergênicos
        """
        allergens = []
        name_lower = name.lower()
        
        # Alergênicos comuns
        if group == "LATICÍNIOS":
            allergens.append("lactose")
        
        if group == "OLEAGINOSAS":
            allergens.append("nuts")
        
        if any(word in name_lower for word in ["trigo", "glúten"]):
            allergens.append("gluten")
        
        if any(word in name_lower for word in ["soja"]):
            allergens.append("soy")
        
        return allergens

