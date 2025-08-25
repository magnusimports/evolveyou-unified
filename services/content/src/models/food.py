"""
Modelos de dados para alimentos
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ServingSize(BaseModel):
    """Tamanho de porção de um alimento"""
    name: str = Field(..., description="Nome da porção (ex: 1 xícara, 100g)")
    weight_grams: float = Field(..., description="Peso em gramas")
    calories: float = Field(..., description="Calorias nesta porção")
    protein: float = Field(..., description="Proteína em gramas")
    carbs: float = Field(..., description="Carboidratos em gramas")
    fat: float = Field(..., description="Gordura em gramas")
    fiber: Optional[float] = Field(None, description="Fibra em gramas")
    sugar: Optional[float] = Field(None, description="Açúcar em gramas")
    sodium: Optional[float] = Field(None, description="Sódio em mg")

class NutritionalInfo(BaseModel):
    """Informações nutricionais por 100g"""
    calories: float = Field(..., description="Calorias por 100g")
    protein: float = Field(..., description="Proteína em gramas por 100g")
    carbs: float = Field(..., description="Carboidratos em gramas por 100g")
    fat: float = Field(..., description="Gordura em gramas por 100g")
    fiber: Optional[float] = Field(None, description="Fibra em gramas por 100g")
    sugar: Optional[float] = Field(None, description="Açúcar em gramas por 100g")
    sodium: Optional[float] = Field(None, description="Sódio em mg por 100g")
    calcium: Optional[float] = Field(None, description="Cálcio em mg por 100g")
    iron: Optional[float] = Field(None, description="Ferro em mg por 100g")
    vitamin_c: Optional[float] = Field(None, description="Vitamina C em mg por 100g")
    vitamin_a: Optional[float] = Field(None, description="Vitamina A em mcg por 100g")

class Food(BaseModel):
    """Modelo de dados para alimentos"""
    id: Optional[str] = Field(None, description="ID único do alimento")
    name: str = Field(..., description="Nome do alimento")
    name_en: Optional[str] = Field(None, description="Nome em inglês")
    category: str = Field(..., description="Categoria do alimento")
    subcategory: Optional[str] = Field(None, description="Subcategoria")
    brand: Optional[str] = Field(None, description="Marca do produto")
    barcode: Optional[str] = Field(None, description="Código de barras")
    
    # Informações nutricionais
    nutritional_info: NutritionalInfo = Field(..., description="Informações nutricionais por 100g")
    serving_sizes: List[ServingSize] = Field(default_factory=list, description="Tamanhos de porção disponíveis")
    
    # Metadados
    description: Optional[str] = Field(None, description="Descrição do alimento")
    ingredients: Optional[List[str]] = Field(None, description="Lista de ingredientes")
    allergens: Optional[List[str]] = Field(None, description="Alérgenos presentes")
    tags: Optional[List[str]] = Field(None, description="Tags para busca")
    
    # Informações de origem
    source: Optional[str] = Field(None, description="Fonte dos dados")
    verified: bool = Field(False, description="Se os dados foram verificados")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FoodSearchResponse(BaseModel):
    """Resposta da busca de alimentos"""
    foods: List[Food] = Field(..., description="Lista de alimentos encontrados")
    total: int = Field(..., description="Total de resultados disponíveis")
    limit: int = Field(..., description="Limite aplicado na busca")
    offset: int = Field(..., description="Offset aplicado na busca")
    has_more: bool = Field(..., description="Se há mais resultados disponíveis")
    
class FoodCreateRequest(BaseModel):
    """Request para criar um novo alimento"""
    name: str = Field(..., description="Nome do alimento")
    category: str = Field(..., description="Categoria do alimento")
    nutritional_info: NutritionalInfo = Field(..., description="Informações nutricionais")
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    serving_sizes: Optional[List[ServingSize]] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None

class FoodUpdateRequest(BaseModel):
    """Request para atualizar um alimento"""
    name: Optional[str] = None
    category: Optional[str] = None
    nutritional_info: Optional[NutritionalInfo] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    serving_sizes: Optional[List[ServingSize]] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    verified: Optional[bool] = None

