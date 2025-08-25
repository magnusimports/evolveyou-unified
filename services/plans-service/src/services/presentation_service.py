"""
Serviço de Apresentação Personalizada de Planos
"""

import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import structlog
from jinja2 import Template

from models.plan import (
    PlanPresentation, DailyTip, ProgressMetric, GoalType, 
    DietPlan, WorkoutPlan, AlgorithmConfig
)
from config.settings import get_settings

logger = structlog.get_logger(__name__)

class PresentationService:
    """Serviço para gerar apresentações personalizadas dos planos"""
    
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.settings = get_settings()
        self.presentation_config = self.settings.presentation_config
        
        # Templates de mensagens motivacionais
        self.motivational_templates = self._load_motivational_templates()
        
        # Templates de resumos diários
        self.summary_templates = self._load_summary_templates()
    
    async def generate_plan_presentation(
        self,
        user_id: str,
        target_date: date,
        diet_plan: Optional[DietPlan] = None,
        workout_plan: Optional[WorkoutPlan] = None
    ) -> PlanPresentation:
        """
        Gera apresentação personalizada do plano do usuário
        
        Args:
            user_id: ID do usuário
            target_date: Data alvo
            diet_plan: Plano de dieta (opcional)
            workout_plan: Plano de treino (opcional)
            
        Returns:
            PlanPresentation: Apresentação personalizada
        """
        logger.info("Gerando apresentação do plano", user_id=user_id, date=target_date)
        
        try:
            # 1. Obter dados do usuário
            user_data = await self._get_user_data(user_id)
            user_name = user_data.get("name", "").split()[0] if user_data.get("name") else None
            goal = GoalType(user_data.get("goal", "manter_peso"))
            
            # 2. Obter planos se não fornecidos
            if not diet_plan:
                diet_plan = await self._get_diet_plan(user_id, target_date)
            if not workout_plan:
                workout_plan = await self._get_workout_plan(user_id, target_date)
            
            # 3. Gerar mensagem motivacional personalizada
            motivational_message = self._generate_motivational_message(user_name, goal, user_data)
            
            # 4. Gerar resumo diário
            daily_summary = self._generate_daily_summary(diet_plan, workout_plan, goal)
            
            # 5. Gerar destaques da dieta
            diet_highlights = self._generate_diet_highlights(diet_plan, goal) if diet_plan else []
            
            # 6. Gerar destaques do treino
            workout_highlights = self._generate_workout_highlights(workout_plan, goal) if workout_plan else []
            
            # 7. Calcular métricas de progresso
            progress_metrics = await self._calculate_progress_metrics(user_id, target_date, user_data)
            
            # 8. Gerar dicas diárias
            daily_tips = self._generate_daily_tips(goal, target_date, user_data)
            
            # 9. Gerar resumo semanal (se aplicável)
            weekly_summary = await self._generate_weekly_progress_summary(user_id, target_date)
            
            # 10. Definir próximo marco
            next_milestone = self._generate_next_milestone(goal, user_data, progress_metrics)
            
            # 11. Gerar nota de encorajamento
            encouragement_note = self._generate_encouragement_note(goal, progress_metrics, user_name)
            
            presentation = PlanPresentation(
                user_id=user_id,
                date=target_date,
                user_name=user_name,
                goal=goal,
                motivational_message=motivational_message,
                daily_summary=daily_summary,
                diet_highlights=diet_highlights,
                workout_highlights=workout_highlights,
                progress_metrics=progress_metrics,
                daily_tips=daily_tips,
                weekly_progress_summary=weekly_summary,
                next_milestone=next_milestone,
                encouragement_note=encouragement_note
            )
            
            # 12. Salvar apresentação para cache
            await self._save_presentation(presentation)
            
            logger.info("Apresentação gerada com sucesso", user_id=user_id)
            return presentation
            
        except Exception as e:
            logger.error("Erro ao gerar apresentação", user_id=user_id, error=str(e))
            raise
    
    def _load_motivational_templates(self) -> Dict[GoalType, List[str]]:
        """Carrega templates de mensagens motivacionais"""
        return {
            GoalType.PERDER_PESO: [
                "Olá {{name}}! 🔥 Hoje é mais um dia para se aproximar do seu peso ideal! Cada escolha saudável conta!",
                "Bom dia, {{name}}! 💪 Você está no caminho certo para transformar seu corpo. Vamos queimar calorias hoje!",
                "{{name}}, sua determinação é inspiradora! 🌟 Hoje vamos focar no déficit calórico e exercícios eficientes!",
                "Oi {{name}}! ⚡ Lembre-se: cada dia é uma nova oportunidade de se tornar a melhor versão de si mesmo!",
                "{{name}}, você está mais forte que ontem! 🚀 Vamos manter o foco na sua jornada de emagrecimento!"
            ],
            GoalType.GANHAR_MASSA: [
                "E aí, {{name}}! 🏗️ Hoje vamos construir músculos! Cada treino e refeição te aproxima do seu objetivo!",
                "Bom dia, {{name}}! 💪 Hora de alimentar seus músculos e treinar com intensidade para o crescimento!",
                "{{name}}, seu corpo está se transformando! 📈 Consistência é a chave para o ganho de massa muscular!",
                "Olá {{name}}! 🔨 Músculos são construídos na academia e na cozinha. Vamos dar tudo hoje!",
                "{{name}}, cada repetição conta! ⚡ Seu futuro eu mais forte agradece pelo esforço de hoje!"
            ],
            GoalType.AUMENTAR_FORCA: [
                "{{name}}, hoje vamos quebrar limites! 💥 Força não é só física, é mental. Você consegue!",
                "Bom dia, {{name}}! ⚡ Cada série te torna mais forte que ontem. Vamos superar recordes!",
                "Olá {{name}}! 🔨 A força verdadeira vem da consistência. Hoje é dia de evoluir!",
                "{{name}}, você é mais forte do que imagina! 🚀 Vamos provar isso no treino de hoje!",
                "E aí, {{name}}! 💪 Força é conquistada rep por rep, série por série. Vamos nessa!"
            ],
            GoalType.MELHORAR_RESISTENCIA: [
                "{{name}}, resistência é sobre não desistir! 🏃 Hoje vamos aumentar sua capacidade cardiovascular!",
                "Bom dia, {{name}}! ❤️ Cada batimento do coração te torna mais resistente. Vamos treinar!",
                "Olá {{name}}! 🌟 Sua capacidade é maior do que você imagina. Vamos descobrir juntos!",
                "{{name}}, a resistência se constrói passo a passo! 🚀 Hoje vamos mais longe que ontem!",
                "E aí, {{name}}! ⚡ Seu corpo é uma máquina incrível. Vamos otimizar sua performance!"
            ],
            GoalType.MANTER_PESO: [
                "{{name}}, manter é tão desafiador quanto conquistar! 🎯 Parabéns pela consistência!",
                "Bom dia, {{name}}! ⚖️ Você encontrou o equilíbrio perfeito. Vamos manter essa harmonia!",
                "Olá {{name}}! 🔄 Consistência é sua maior aliada na manutenção. Continue assim!",
                "{{name}}, você é um exemplo de disciplina! 🌟 Hoje vamos manter o que conquistou!",
                "E aí, {{name}}! 💪 Manutenção é sobre estilo de vida saudável. Você dominou isso!"
            ]
        }
    
    def _load_summary_templates(self) -> Dict[str, str]:
        """Carrega templates de resumos diários"""
        return {
            "diet_workout": "Hoje você tem um plano completo: {{diet_calories}} calorias distribuídas em {{meal_count}} refeições e {{workout_duration}} minutos de treino focado em {{muscle_groups}}.",
            "diet_only": "Seu plano nutricional de hoje inclui {{diet_calories}} calorias em {{meal_count}} refeições balanceadas para {{goal_description}}.",
            "workout_only": "Treino de {{workout_duration}} minutos focado em {{muscle_groups}} te espera hoje. {{workout_type}} será o foco!",
            "rest_day": "Hoje é seu dia de recuperação! {{active_recovery}} Lembre-se: o descanso é quando seus músculos crescem.",
            "no_plans": "Vamos planejar seu dia! Que tal começar definindo suas metas de alimentação e exercícios?"
        }
    
    def _generate_motivational_message(self, user_name: Optional[str], goal: GoalType, user_data: dict) -> str:
        """Gera mensagem motivacional personalizada"""
        templates = self.motivational_templates.get(goal, self.motivational_templates[GoalType.MANTER_PESO])
        template_str = random.choice(templates)
        
        # Usar nome ou tratamento genérico
        name = user_name if user_name else "Guerreiro(a)"
        
        template = Template(template_str)
        return template.render(name=name)
    
    def _generate_daily_summary(self, diet_plan: Optional[DietPlan], workout_plan: Optional[WorkoutPlan], goal: GoalType) -> str:
        """Gera resumo diário dos planos"""
        goal_descriptions = {
            GoalType.PERDER_PESO: "perda de peso",
            GoalType.GANHAR_MASSA: "ganho de massa muscular",
            GoalType.AUMENTAR_FORCA: "aumento de força",
            GoalType.MELHORAR_RESISTENCIA: "melhora da resistência",
            GoalType.MANTER_PESO: "manutenção do peso"
        }
        
        # Determinar template baseado nos planos disponíveis
        if diet_plan and workout_plan and not workout_plan.rest_day:
            template_key = "diet_workout"
            context = {
                "diet_calories": int(diet_plan.total_calories),
                "meal_count": len(diet_plan.meals),
                "workout_duration": workout_plan.total_estimated_duration_minutes,
                "muscle_groups": ", ".join(workout_plan.sessions[0].muscle_groups_focus[:2]) if workout_plan.sessions else "corpo todo"
            }
        elif diet_plan and (not workout_plan or workout_plan.rest_day):
            template_key = "diet_only"
            context = {
                "diet_calories": int(diet_plan.total_calories),
                "meal_count": len(diet_plan.meals),
                "goal_description": goal_descriptions[goal]
            }
        elif workout_plan and not workout_plan.rest_day:
            template_key = "workout_only"
            context = {
                "workout_duration": workout_plan.total_estimated_duration_minutes,
                "muscle_groups": ", ".join(workout_plan.sessions[0].muscle_groups_focus[:2]) if workout_plan.sessions else "corpo todo",
                "workout_type": workout_plan.sessions[0].workout_type.value.title() if workout_plan.sessions else "Treino"
            }
        elif workout_plan and workout_plan.rest_day:
            template_key = "rest_day"
            context = {
                "active_recovery": workout_plan.active_recovery or "Relaxe e recupere-se."
            }
        else:
            template_key = "no_plans"
            context = {}
        
        template_str = self.summary_templates[template_key]
        template = Template(template_str)
        return template.render(**context)
    
    def _generate_diet_highlights(self, diet_plan: DietPlan, goal: GoalType) -> List[str]:
        """Gera destaques do plano de dieta"""
        highlights = []
        
        # Destaque calórico
        highlights.append(f"🎯 Meta calórica: {int(diet_plan.total_calories)} kcal")
        
        # Destaque proteico
        protein_per_kg = diet_plan.total_protein / 70  # Assumindo 70kg médio
        highlights.append(f"💪 Proteína: {diet_plan.total_protein:.0f}g ({protein_per_kg:.1f}g/kg)")
        
        # Destaque específico por objetivo
        if goal == GoalType.PERDER_PESO:
            highlights.append("🔥 Plano otimizado para déficit calórico")
        elif goal == GoalType.GANHAR_MASSA:
            highlights.append("🏗️ Superávit calórico para crescimento muscular")
        elif goal == GoalType.AUMENTAR_FORCA:
            highlights.append("⚡ Nutrição para performance e força")
        
        # Destaque de variedade
        unique_foods = len(set(food.name for meal in diet_plan.meals for food in meal.foods))
        highlights.append(f"🌈 {unique_foods} alimentos diferentes para variedade")
        
        # Destaque de hidratação
        if diet_plan.water_intake_ml:
            highlights.append(f"💧 Meta de hidratação: {diet_plan.water_intake_ml}ml")
        
        return highlights[:4]  # Máximo 4 destaques
    
    def _generate_workout_highlights(self, workout_plan: WorkoutPlan, goal: GoalType) -> List[str]:
        """Gera destaques do plano de treino"""
        if workout_plan.rest_day:
            return ["🛌 Dia de recuperação - essencial para o progresso!"]
        
        highlights = []
        
        if workout_plan.sessions:
            session = workout_plan.sessions[0]
            
            # Destaque de duração
            highlights.append(f"⏱️ Duração: {workout_plan.total_estimated_duration_minutes} minutos")
            
            # Destaque de grupos musculares
            muscle_groups = ", ".join(session.muscle_groups_focus[:3])
            highlights.append(f"🎯 Foco: {muscle_groups}")
            
            # Destaque de exercícios
            exercise_count = len(session.exercises)
            highlights.append(f"💪 {exercise_count} exercícios selecionados")
            
            # Destaque específico por objetivo
            if goal == GoalType.PERDER_PESO:
                highlights.append("🔥 Treino para máxima queima calórica")
            elif goal == GoalType.GANHAR_MASSA:
                highlights.append("🏗️ Volume otimizado para hipertrofia")
            elif goal == GoalType.AUMENTAR_FORCA:
                highlights.append("⚡ Intensidade alta para ganhos de força")
            elif goal == GoalType.MELHORAR_RESISTENCIA:
                highlights.append("🏃 Treino cardiovascular e resistência")
            
            # Destaque de equipamentos
            if session.equipment_needed:
                equipment = ", ".join(session.equipment_needed[:2])
                highlights.append(f"🏋️ Equipamentos: {equipment}")
        
        return highlights[:4]  # Máximo 4 destaques
    
    async def _calculate_progress_metrics(self, user_id: str, target_date: date, user_data: dict) -> List[ProgressMetric]:
        """Calcula métricas de progresso do usuário"""
        metrics = []
        
        try:
            # Métrica de peso (se disponível)
            weight_data = await self._get_weight_progress(user_id, target_date)
            if weight_data:
                metrics.append(ProgressMetric(
                    metric_name="Peso",
                    current_value=weight_data["current"],
                    target_value=weight_data.get("target"),
                    unit="kg",
                    trend=weight_data.get("trend", "stable"),
                    percentage_change=weight_data.get("percentage_change")
                ))
            
            # Métrica de aderência aos planos
            adherence_data = await self._get_adherence_metrics(user_id, target_date)
            if adherence_data:
                metrics.append(ProgressMetric(
                    metric_name="Aderência aos Planos",
                    current_value=adherence_data["current"] * 100,
                    target_value=85.0,  # Meta de 85%
                    unit="%",
                    trend="up" if adherence_data["current"] > 0.8 else "stable"
                ))
            
            # Métrica de calorias médias
            calorie_data = await self._get_calorie_metrics(user_id, target_date)
            if calorie_data:
                metrics.append(ProgressMetric(
                    metric_name="Calorias Médias",
                    current_value=calorie_data["average"],
                    target_value=calorie_data.get("target"),
                    unit="kcal",
                    trend=calorie_data.get("trend", "stable")
                ))
            
            # Métrica de treinos por semana
            workout_data = await self._get_workout_frequency(user_id, target_date)
            if workout_data:
                metrics.append(ProgressMetric(
                    metric_name="Treinos por Semana",
                    current_value=workout_data["current"],
                    target_value=workout_data.get("target", 4),
                    unit="treinos",
                    trend="up" if workout_data["current"] >= workout_data.get("target", 4) else "stable"
                ))
            
        except Exception as e:
            logger.error("Erro ao calcular métricas de progresso", error=str(e))
        
        return metrics[:3]  # Máximo 3 métricas principais
    
    def _generate_daily_tips(self, goal: GoalType, target_date: date, user_data: dict) -> List[DailyTip]:
        """Gera dicas diárias personalizadas"""
        tips_database = {
            GoalType.PERDER_PESO: [
                DailyTip(category="nutrition", title="Hidratação", content="Beba água antes das refeições para aumentar a saciedade", priority=1),
                DailyTip(category="training", title="Cardio", content="Inclua 10 minutos de caminhada após as refeições", priority=2),
                DailyTip(category="lifestyle", title="Sono", content="Durma 7-8 horas para otimizar hormônios da saciedade", priority=1),
                DailyTip(category="motivation", title="Progresso", content="Tire fotos do progresso, não apenas se pese", priority=2)
            ],
            GoalType.GANHAR_MASSA: [
                DailyTip(category="nutrition", title="Proteína", content="Consuma proteína a cada 3-4 horas para síntese muscular", priority=1),
                DailyTip(category="training", title="Sobrecarga", content="Aumente gradualmente peso ou repetições", priority=1),
                DailyTip(category="lifestyle", title="Recuperação", content="Durma 8-9 horas para máxima recuperação muscular", priority=1),
                DailyTip(category="motivation", title="Paciência", content="Ganho de massa é processo lento, seja consistente", priority=2)
            ],
            GoalType.AUMENTAR_FORCA: [
                DailyTip(category="training", title="Técnica", content="Priorize técnica perfeita antes de aumentar carga", priority=1),
                DailyTip(category="training", title="Descanso", content="Descanse 2-3 minutos entre séries pesadas", priority=1),
                DailyTip(category="nutrition", title="Energia", content="Consuma carboidratos antes do treino de força", priority=2),
                DailyTip(category="lifestyle", title="Registro", content="Anote seus pesos para acompanhar progressão", priority=2)
            ],
            GoalType.MELHORAR_RESISTENCIA: [
                DailyTip(category="training", title="Progressão", content="Aumente gradualmente duração ou intensidade", priority=1),
                DailyTip(category="nutrition", title="Hidratação", content="Mantenha-se hidratado durante exercícios longos", priority=1),
                DailyTip(category="training", title="Variedade", content="Alterne entre diferentes tipos de cardio", priority=2),
                DailyTip(category="lifestyle", title="Recuperação", content="Inclua dias de recuperação ativa", priority=2)
            ],
            GoalType.MANTER_PESO: [
                DailyTip(category="lifestyle", title="Equilíbrio", content="Mantenha flexibilidade na dieta sem exageros", priority=1),
                DailyTip(category="training", title="Variedade", content="Varie treinos para manter motivação", priority=2),
                DailyTip(category="nutrition", title="Monitoramento", content="Monitore peso semanalmente, não diariamente", priority=2),
                DailyTip(category="motivation", title="Sustentabilidade", content="Foque em hábitos sustentáveis a longo prazo", priority=1)
            ]
        }
        
        goal_tips = tips_database.get(goal, tips_database[GoalType.MANTER_PESO])
        
        # Selecionar 2-3 dicas aleatórias, priorizando as de alta prioridade
        high_priority = [tip for tip in goal_tips if tip.priority == 1]
        low_priority = [tip for tip in goal_tips if tip.priority == 2]
        
        selected_tips = []
        if high_priority:
            selected_tips.append(random.choice(high_priority))
        if low_priority and len(selected_tips) < 2:
            selected_tips.append(random.choice(low_priority))
        
        return selected_tips
    
    async def _generate_weekly_progress_summary(self, user_id: str, target_date: date) -> Optional[str]:
        """Gera resumo de progresso semanal"""
        try:
            # Verificar se é domingo (fim de semana)
            if target_date.weekday() != 6:  # 6 = domingo
                return None
            
            week_start = target_date - timedelta(days=6)
            
            # Obter dados da semana
            weekly_data = await self._get_weekly_data(user_id, week_start, target_date)
            
            if not weekly_data:
                return None
            
            # Gerar resumo baseado nos dados
            summary_parts = []
            
            if weekly_data.get("workouts_completed", 0) > 0:
                summary_parts.append(f"Você completou {weekly_data['workouts_completed']} treinos esta semana")
            
            if weekly_data.get("diet_adherence", 0) > 0.7:
                summary_parts.append(f"Manteve {weekly_data['diet_adherence']*100:.0f}% de aderência à dieta")
            
            if weekly_data.get("weight_change"):
                change = weekly_data["weight_change"]
                if abs(change) >= 0.2:  # Mudança significativa
                    direction = "perdeu" if change < 0 else "ganhou"
                    summary_parts.append(f"{direction} {abs(change):.1f}kg")
            
            if summary_parts:
                return "Resumo da semana: " + ", ".join(summary_parts) + ". Continue assim! 🎉"
            
            return "Semana concluída! Continue focado nos seus objetivos! 💪"
            
        except Exception as e:
            logger.error("Erro ao gerar resumo semanal", error=str(e))
            return None
    
    def _generate_next_milestone(self, goal: GoalType, user_data: dict, metrics: List[ProgressMetric]) -> str:
        """Gera próximo marco/objetivo"""
        milestones = {
            GoalType.PERDER_PESO: [
                "Perder mais 1kg nas próximas 2 semanas",
                "Completar 5 treinos na próxima semana",
                "Manter déficit calórico por 7 dias consecutivos"
            ],
            GoalType.GANHAR_MASSA: [
                "Ganhar 0.5kg de massa muscular no próximo mês",
                "Aumentar carga em 5% nos exercícios principais",
                "Manter superávit calórico por 2 semanas"
            ],
            GoalType.AUMENTAR_FORCA: [
                "Aumentar 5kg no supino nas próximas 3 semanas",
                "Completar todas as séries com carga atual",
                "Melhorar técnica em exercícios compostos"
            ],
            GoalType.MELHORAR_RESISTENCIA: [
                "Correr 5km sem parar nas próximas 4 semanas",
                "Aumentar duração do cardio em 10 minutos",
                "Reduzir frequência cardíaca de repouso"
            ],
            GoalType.MANTER_PESO: [
                "Manter peso estável por mais 2 semanas",
                "Experimentar 3 novos exercícios este mês",
                "Manter aderência de 85% aos planos"
            ]
        }
        
        goal_milestones = milestones.get(goal, milestones[GoalType.MANTER_PESO])
        return random.choice(goal_milestones)
    
    def _generate_encouragement_note(self, goal: GoalType, metrics: List[ProgressMetric], user_name: Optional[str]) -> str:
        """Gera nota de encorajamento personalizada"""
        name = user_name if user_name else "Guerreiro(a)"
        
        # Analisar métricas para personalizar encorajamento
        positive_trends = sum(1 for metric in metrics if metric.trend == "up")
        
        if positive_trends >= 2:
            encouragements = [
                f"Parabéns, {name}! Seus resultados mostram progresso consistente! 🌟",
                f"{name}, você está no caminho certo! Continue com essa dedicação! 🚀",
                f"Excelente trabalho, {name}! Seus esforços estão dando frutos! 💪"
            ]
        elif positive_trends == 1:
            encouragements = [
                f"{name}, você está evoluindo! Pequenos passos levam a grandes conquistas! 📈",
                f"Continue assim, {name}! O progresso está acontecendo! ⭐",
                f"{name}, cada dia é uma vitória! Você está mais forte! 💪"
            ]
        else:
            encouragements = [
                f"{name}, lembre-se: progresso não é sempre linear. Continue firme! 🔥",
                f"Não desista, {name}! Os melhores resultados vêm da consistência! 💪",
                f"{name}, você é mais forte do que qualquer desafio! Vamos juntos! 🌟"
            ]
        
        return random.choice(encouragements)
    
    # Métodos auxiliares para obter dados
    
    async def _get_user_data(self, user_id: str) -> dict:
        """Obtém dados do usuário"""
        try:
            doc_ref = self.firebase_service.db.collection("users").document(user_id)
            doc = await doc_ref.get()
            return doc.to_dict() if doc.exists else {}
        except Exception as e:
            logger.error("Erro ao obter dados do usuário", error=str(e))
            return {}
    
    async def _get_diet_plan(self, user_id: str, target_date: date) -> Optional[DietPlan]:
        """Obtém plano de dieta"""
        try:
            doc_ref = self.firebase_service.db.collection("diet_plans").document(f"{user_id}_{target_date}")
            doc = await doc_ref.get()
            if doc.exists:
                return DietPlan(**doc.to_dict())
            return None
        except Exception as e:
            logger.error("Erro ao obter plano de dieta", error=str(e))
            return None
    
    async def _get_workout_plan(self, user_id: str, target_date: date) -> Optional[WorkoutPlan]:
        """Obtém plano de treino"""
        try:
            doc_ref = self.firebase_service.db.collection("workout_plans").document(f"{user_id}_{target_date}")
            doc = await doc_ref.get()
            if doc.exists:
                return WorkoutPlan(**doc.to_dict())
            return None
        except Exception as e:
            logger.error("Erro ao obter plano de treino", error=str(e))
            return None
    
    async def _get_weight_progress(self, user_id: str, target_date: date) -> Optional[dict]:
        """Obtém progresso de peso"""
        try:
            # Buscar últimas medições de peso
            query = (self.firebase_service.db.collection("weight_measurements")
                    .where("user_id", "==", user_id)
                    .order_by("date", direction="desc")
                    .limit(2))
            
            docs = await query.get()
            
            if len(docs) >= 1:
                current = docs[0].to_dict()
                previous = docs[1].to_dict() if len(docs) > 1 else None
                
                result = {"current": current["weight"]}
                
                if previous:
                    change = current["weight"] - previous["weight"]
                    result["percentage_change"] = (change / previous["weight"]) * 100
                    result["trend"] = "down" if change < -0.1 else "up" if change > 0.1 else "stable"
                
                return result
            
            return None
        except Exception as e:
            logger.error("Erro ao obter progresso de peso", error=str(e))
            return None
    
    async def _get_adherence_metrics(self, user_id: str, target_date: date) -> Optional[dict]:
        """Obtém métricas de aderência"""
        try:
            # Calcular aderência dos últimos 7 dias
            week_start = target_date - timedelta(days=6)
            
            # Contar planos seguidos vs. planos criados
            plans_query = (self.firebase_service.db.collection("diet_plans")
                          .where("user_id", "==", user_id)
                          .where("date", ">=", week_start)
                          .where("date", "<=", target_date))
            
            plans_docs = await plans_query.get()
            
            if plans_docs:
                total_plans = len(plans_docs)
                # Simular aderência baseada em dados disponíveis
                adherence = min(0.9, total_plans / 7.0)  # Máximo 90%
                
                return {"current": adherence}
            
            return None
        except Exception as e:
            logger.error("Erro ao obter métricas de aderência", error=str(e))
            return None
    
    async def _get_calorie_metrics(self, user_id: str, target_date: date) -> Optional[dict]:
        """Obtém métricas de calorias"""
        try:
            # Buscar planos dos últimos 7 dias
            week_start = target_date - timedelta(days=6)
            
            query = (self.firebase_service.db.collection("diet_plans")
                    .where("user_id", "==", user_id)
                    .where("date", ">=", week_start)
                    .where("date", "<=", target_date))
            
            docs = await query.get()
            
            if docs:
                calories = [doc.to_dict()["total_calories"] for doc in docs]
                average = sum(calories) / len(calories)
                
                return {
                    "average": average,
                    "target": calories[-1] if calories else None,  # Última meta
                    "trend": "stable"
                }
            
            return None
        except Exception as e:
            logger.error("Erro ao obter métricas de calorias", error=str(e))
            return None
    
    async def _get_workout_frequency(self, user_id: str, target_date: date) -> Optional[dict]:
        """Obtém frequência de treinos"""
        try:
            # Contar treinos da semana atual
            week_start = target_date - timedelta(days=target_date.weekday())
            
            query = (self.firebase_service.db.collection("workout_plans")
                    .where("user_id", "==", user_id)
                    .where("date", ">=", week_start)
                    .where("date", "<=", target_date)
                    .where("rest_day", "==", False))
            
            docs = await query.get()
            
            return {
                "current": len(docs),
                "target": 4  # Meta padrão de 4 treinos por semana
            }
            
        except Exception as e:
            logger.error("Erro ao obter frequência de treinos", error=str(e))
            return None
    
    async def _get_weekly_data(self, user_id: str, week_start: date, week_end: date) -> Optional[dict]:
        """Obtém dados da semana"""
        try:
            # Buscar dados da semana
            workouts_query = (self.firebase_service.db.collection("workout_plans")
                             .where("user_id", "==", user_id)
                             .where("date", ">=", week_start)
                             .where("date", "<=", week_end)
                             .where("rest_day", "==", False))
            
            workout_docs = await workouts_query.get()
            
            return {
                "workouts_completed": len(workout_docs),
                "diet_adherence": 0.8,  # Simular 80% de aderência
                "weight_change": None  # Seria calculado com dados reais
            }
            
        except Exception as e:
            logger.error("Erro ao obter dados semanais", error=str(e))
            return None
    
    async def _save_presentation(self, presentation: PlanPresentation):
        """Salva apresentação no cache"""
        try:
            doc_id = f"{presentation.user_id}_{presentation.date}"
            doc_ref = self.firebase_service.db.collection("plan_presentations").document(doc_id)
            
            presentation_data = presentation.dict()
            presentation_data["created_at"] = datetime.utcnow()
            
            await doc_ref.set(presentation_data)
            
        except Exception as e:
            logger.error("Erro ao salvar apresentação", error=str(e))

