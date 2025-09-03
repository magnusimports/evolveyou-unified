// Anamnese Nutricional Completa - 22 Perguntas Inteligentes
export const anamneseQuestions = [
  {
    id: 'personal_info',
    title: 'Informações Pessoais',
    type: 'form',
    fields: [
      {
        id: 'age',
        label: 'Idade',
        type: 'number',
        placeholder: 'Ex: 25',
        required: true,
        min: 16,
        max: 100
      },
      {
        id: 'gender',
        label: 'Sexo',
        type: 'select',
        required: true,
        options: [
          { value: 'male', label: 'Masculino' },
          { value: 'female', label: 'Feminino' },
          { value: 'other', label: 'Outro' }
        ]
      },
      {
        id: 'height',
        label: 'Altura (cm)',
        type: 'number',
        placeholder: 'Ex: 170',
        required: true,
        min: 100,
        max: 250
      },
      {
        id: 'weight',
        label: 'Peso atual (kg)',
        type: 'number',
        placeholder: 'Ex: 70',
        required: true,
        min: 30,
        max: 300,
        step: 0.1
      }
    ]
  },
  {
    id: 'activity_level',
    title: 'Qual seu nível de atividade física?',
    subtitle: 'Isso nos ajuda a calcular seu gasto energético',
    type: 'single_choice',
    options: [
      {
        id: 'sedentary',
        label: 'Sedentário',
        description: 'Pouco ou nenhum exercício',
        multiplier: 1.2
      },
      {
        id: 'light',
        label: 'Levemente Ativo',
        description: 'Exercício leve 1-3 dias/semana',
        multiplier: 1.375
      },
      {
        id: 'moderate',
        label: 'Moderadamente Ativo',
        description: 'Exercício moderado 3-5 dias/semana',
        multiplier: 1.55
      },
      {
        id: 'very_active',
        label: 'Muito Ativo',
        description: 'Exercício intenso 6-7 dias/semana',
        multiplier: 1.725
      },
      {
        id: 'extremely_active',
        label: 'Extremamente Ativo',
        description: 'Exercício muito intenso, trabalho físico',
        multiplier: 1.9
      }
    ]
  },
  {
    id: 'primary_goal',
    title: 'Qual seu objetivo principal?',
    subtitle: 'Vamos personalizar tudo baseado no seu foco',
    type: 'single_choice',
    options: [
      {
        id: 'weight_loss',
        label: 'Perder Peso',
        description: 'Reduzir gordura corporal',
        icon: 'TrendingDown'
      },
      {
        id: 'muscle_gain',
        label: 'Ganhar Massa Muscular',
        description: 'Aumentar músculos e força',
        icon: 'Target'
      },
      {
        id: 'maintenance',
        label: 'Manter Peso',
        description: 'Manter peso atual e melhorar composição',
        icon: 'Shield'
      },
      {
        id: 'performance',
        label: 'Performance Esportiva',
        description: 'Melhorar rendimento atlético',
        icon: 'Zap'
      }
    ]
  },
  {
    id: 'target_weight',
    title: 'Qual seu peso ideal?',
    subtitle: 'Meta realista baseada na sua altura e biotipo',
    type: 'form',
    fields: [
      {
        id: 'target_weight',
        label: 'Peso meta (kg)',
        type: 'number',
        placeholder: 'Ex: 65',
        required: true,
        min: 30,
        max: 300,
        step: 0.1
      },
      {
        id: 'timeline',
        label: 'Em quanto tempo?',
        type: 'select',
        required: true,
        options: [
          { value: '1_month', label: '1 mês' },
          { value: '3_months', label: '3 meses' },
          { value: '6_months', label: '6 meses' },
          { value: '1_year', label: '1 ano' },
          { value: 'no_rush', label: 'Sem pressa' }
        ]
      }
    ]
  },
  {
    id: 'dietary_restrictions',
    title: 'Você tem alguma restrição alimentar?',
    subtitle: 'Vamos respeitar suas necessidades e preferências',
    type: 'multiple_choice',
    options: [
      { id: 'none', label: 'Nenhuma restrição' },
      { id: 'vegetarian', label: 'Vegetariano' },
      { id: 'vegan', label: 'Vegano' },
      { id: 'lactose_intolerant', label: 'Intolerante à lactose' },
      { id: 'gluten_intolerant', label: 'Intolerante ao glúten/celíaco' },
      { id: 'diabetes', label: 'Diabetes' },
      { id: 'hypertension', label: 'Hipertensão' },
      { id: 'food_allergies', label: 'Alergias alimentares específicas' }
    ]
  },
  {
    id: 'meal_frequency',
    title: 'Quantas refeições você faz por dia?',
    subtitle: 'Vamos adequar o plano à sua rotina',
    type: 'single_choice',
    options: [
      { id: '3_meals', label: '3 refeições', description: 'Café, almoço e jantar' },
      { id: '4_meals', label: '4 refeições', description: '+ 1 lanche' },
      { id: '5_meals', label: '5 refeições', description: '+ 2 lanches' },
      { id: '6_meals', label: '6 refeições', description: '+ 3 lanches' }
    ]
  },
  {
    id: 'water_intake',
    title: 'Quanta água você bebe por dia?',
    subtitle: 'Hidratação é fundamental para o metabolismo',
    type: 'single_choice',
    options: [
      { id: 'less_1l', label: 'Menos de 1 litro', description: 'Precisa melhorar muito' },
      { id: '1_2l', label: '1-2 litros', description: 'Abaixo do recomendado' },
      { id: '2_3l', label: '2-3 litros', description: 'Quantidade adequada' },
      { id: 'more_3l', label: 'Mais de 3 litros', description: 'Excelente hidratação' }
    ]
  },
  {
    id: 'sleep_quality',
    title: 'Como é a qualidade do seu sono?',
    subtitle: 'O sono afeta diretamente o metabolismo e a fome',
    type: 'form',
    fields: [
      {
        id: 'sleep_hours',
        label: 'Horas de sono por noite',
        type: 'number',
        placeholder: 'Ex: 7',
        required: true,
        min: 3,
        max: 12
      },
      {
        id: 'sleep_quality',
        label: 'Qualidade do sono',
        type: 'select',
        required: true,
        options: [
          { value: 'excellent', label: 'Excelente - acordo descansado' },
          { value: 'good', label: 'Boa - acordo bem na maioria dos dias' },
          { value: 'fair', label: 'Regular - acordo cansado às vezes' },
          { value: 'poor', label: 'Ruim - acordo cansado frequentemente' }
        ]
      }
    ]
  },
  {
    id: 'stress_level',
    title: 'Como está seu nível de estresse?',
    subtitle: 'O estresse influencia o cortisol e o armazenamento de gordura',
    type: 'single_choice',
    options: [
      { id: 'low', label: 'Baixo', description: 'Raramente me sinto estressado' },
      { id: 'moderate', label: 'Moderado', description: 'Estresse ocasional e controlável' },
      { id: 'high', label: 'Alto', description: 'Frequentemente estressado' },
      { id: 'very_high', label: 'Muito Alto', description: 'Estresse constante e intenso' }
    ]
  },
  {
    id: 'cooking_skills',
    title: 'Como você avalia suas habilidades culinárias?',
    subtitle: 'Vamos adequar as receitas ao seu nível',
    type: 'single_choice',
    options: [
      { id: 'beginner', label: 'Iniciante', description: 'Preparo básico, receitas simples' },
      { id: 'intermediate', label: 'Intermediário', description: 'Cozinho regularmente' },
      { id: 'advanced', label: 'Avançado', description: 'Gosto de receitas elaboradas' },
      { id: 'no_time', label: 'Sem tempo', description: 'Prefiro praticidade' }
    ]
  },
  {
    id: 'meal_prep_time',
    title: 'Quanto tempo você tem para preparar refeições?',
    subtitle: 'Vamos sugerir receitas adequadas ao seu tempo',
    type: 'single_choice',
    options: [
      { id: 'less_15min', label: 'Menos de 15 min', description: 'Refeições super rápidas' },
      { id: '15_30min', label: '15-30 minutos', description: 'Preparo moderado' },
      { id: '30_60min', label: '30-60 minutos', description: 'Posso cozinhar com calma' },
      { id: 'more_60min', label: 'Mais de 1 hora', description: 'Adoro cozinhar' }
    ]
  },
  {
    id: 'budget_range',
    title: 'Qual sua faixa de orçamento mensal para alimentação?',
    subtitle: 'Vamos sugerir alimentos que cabem no seu bolso',
    type: 'single_choice',
    options: [
      { id: 'low', label: 'Até R$ 300', description: 'Orçamento apertado' },
      { id: 'moderate', label: 'R$ 300-600', description: 'Orçamento moderado' },
      { id: 'comfortable', label: 'R$ 600-1000', description: 'Orçamento confortável' },
      { id: 'flexible', label: 'Acima de R$ 1000', description: 'Orçamento flexível' }
    ]
  },
  {
    id: 'favorite_foods',
    title: 'Quais são seus alimentos favoritos?',
    subtitle: 'Vamos incluir o que você gosta no seu plano',
    type: 'multiple_choice',
    options: [
      { id: 'rice_beans', label: 'Arroz e feijão' },
      { id: 'chicken', label: 'Frango' },
      { id: 'fish', label: 'Peixes' },
      { id: 'beef', label: 'Carne vermelha' },
      { id: 'eggs', label: 'Ovos' },
      { id: 'fruits', label: 'Frutas' },
      { id: 'vegetables', label: 'Vegetais' },
      { id: 'pasta', label: 'Massas' },
      { id: 'dairy', label: 'Laticínios' },
      { id: 'nuts', label: 'Castanhas e nozes' }
    ]
  },
  {
    id: 'eating_out_frequency',
    title: 'Com que frequência você come fora de casa?',
    subtitle: 'Vamos dar dicas para essas ocasiões',
    type: 'single_choice',
    options: [
      { id: 'rarely', label: 'Raramente', description: 'Menos de 1x por semana' },
      { id: 'weekly', label: 'Semanalmente', description: '1-2x por semana' },
      { id: 'frequently', label: 'Frequentemente', description: '3-4x por semana' },
      { id: 'daily', label: 'Diariamente', description: 'Quase todos os dias' }
    ]
  },
  {
    id: 'supplement_usage',
    title: 'Você usa algum suplemento atualmente?',
    subtitle: 'Vamos considerar na sua estratégia nutricional',
    type: 'multiple_choice',
    options: [
      { id: 'none', label: 'Não uso suplementos' },
      { id: 'whey_protein', label: 'Whey Protein' },
      { id: 'creatine', label: 'Creatina' },
      { id: 'multivitamin', label: 'Multivitamínico' },
      { id: 'omega3', label: 'Ômega 3' },
      { id: 'vitamin_d', label: 'Vitamina D' },
      { id: 'bcaa', label: 'BCAA' },
      { id: 'pre_workout', label: 'Pré-treino' },
      { id: 'others', label: 'Outros' }
    ]
  },
  {
    id: 'health_conditions',
    title: 'Você tem alguma condição de saúde?',
    subtitle: 'Informações importantes para personalização segura',
    type: 'multiple_choice',
    options: [
      { id: 'none', label: 'Nenhuma condição' },
      { id: 'diabetes_type1', label: 'Diabetes Tipo 1' },
      { id: 'diabetes_type2', label: 'Diabetes Tipo 2' },
      { id: 'hypertension', label: 'Hipertensão' },
      { id: 'hypothyroidism', label: 'Hipotireoidismo' },
      { id: 'hyperthyroidism', label: 'Hipertireoidismo' },
      { id: 'pcos', label: 'SOP (Síndrome dos Ovários Policísticos)' },
      { id: 'heart_disease', label: 'Doença cardíaca' },
      { id: 'kidney_disease', label: 'Doença renal' },
      { id: 'others', label: 'Outras condições' }
    ]
  },
  {
    id: 'medications',
    title: 'Você toma algum medicamento regularmente?',
    subtitle: 'Alguns medicamentos podem afetar o metabolismo',
    type: 'text_area',
    placeholder: 'Liste os medicamentos que você toma regularmente...'
  },
  {
    id: 'previous_diets',
    title: 'Você já fez alguma dieta antes?',
    subtitle: 'Vamos aprender com experiências passadas',
    type: 'multiple_choice',
    options: [
      { id: 'none', label: 'Nunca fiz dieta' },
      { id: 'low_carb', label: 'Low Carb' },
      { id: 'keto', label: 'Cetogênica' },
      { id: 'intermittent_fasting', label: 'Jejum Intermitente' },
      { id: 'paleo', label: 'Paleo' },
      { id: 'mediterranean', label: 'Mediterrânea' },
      { id: 'vegetarian', label: 'Vegetariana' },
      { id: 'calorie_counting', label: 'Contagem de calorias' },
      { id: 'others', label: 'Outras dietas' }
    ]
  },
  {
    id: 'diet_challenges',
    title: 'Quais são seus maiores desafios com alimentação?',
    subtitle: 'Vamos focar em resolver esses pontos',
    type: 'multiple_choice',
    options: [
      { id: 'cravings', label: 'Compulsão/vontade de comer doces' },
      { id: 'portion_control', label: 'Controle de porções' },
      { id: 'meal_planning', label: 'Planejamento de refeições' },
      { id: 'time_management', label: 'Falta de tempo' },
      { id: 'social_eating', label: 'Comer em eventos sociais' },
      { id: 'emotional_eating', label: 'Comer emocional' },
      { id: 'consistency', label: 'Manter consistência' },
      { id: 'motivation', label: 'Falta de motivação' }
    ]
  },
  {
    id: 'success_metrics',
    title: 'Como você gostaria de acompanhar seu progresso?',
    subtitle: 'Vamos focar nas métricas que mais te motivam',
    type: 'multiple_choice',
    options: [
      { id: 'weight', label: 'Peso na balança' },
      { id: 'body_measurements', label: 'Medidas corporais' },
      { id: 'photos', label: 'Fotos de progresso' },
      { id: 'energy_levels', label: 'Níveis de energia' },
      { id: 'sleep_quality', label: 'Qualidade do sono' },
      { id: 'workout_performance', label: 'Performance nos treinos' },
      { id: 'mood', label: 'Humor e bem-estar' },
      { id: 'blood_tests', label: 'Exames de sangue' }
    ]
  }
];

// Função para calcular BMR (Taxa Metabólica Basal)
export const calculateBMR = (weight, height, age, gender) => {
  if (gender === 'male') {
    return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
  } else {
    return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
  }
};

// Função para calcular TDEE (Gasto Energético Total Diário)
export const calculateTDEE = (bmr, activityLevel) => {
  const multipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    very_active: 1.725,
    extremely_active: 1.9
  };
  
  return bmr * (multipliers[activityLevel] || 1.2);
};

// Função para calcular IMC
export const calculateBMI = (weight, height) => {
  const heightInMeters = height / 100;
  return weight / (heightInMeters * heightInMeters);
};

// Função para classificar IMC
export const classifyBMI = (bmi) => {
  if (bmi < 18.5) return { category: 'Abaixo do peso', color: 'text-blue-500' };
  if (bmi < 25) return { category: 'Peso normal', color: 'text-green-500' };
  if (bmi < 30) return { category: 'Sobrepeso', color: 'text-yellow-500' };
  return { category: 'Obesidade', color: 'text-red-500' };
};

// Função para calcular distribuição de macronutrientes
export const calculateMacros = (calories, goal) => {
  let proteinPercent, carbPercent, fatPercent;
  
  switch (goal) {
    case 'weight_loss':
      proteinPercent = 0.30;
      carbPercent = 0.35;
      fatPercent = 0.35;
      break;
    case 'muscle_gain':
      proteinPercent = 0.25;
      carbPercent = 0.45;
      fatPercent = 0.30;
      break;
    case 'maintenance':
      proteinPercent = 0.25;
      carbPercent = 0.40;
      fatPercent = 0.35;
      break;
    case 'performance':
      proteinPercent = 0.20;
      carbPercent = 0.50;
      fatPercent = 0.30;
      break;
    default:
      proteinPercent = 0.25;
      carbPercent = 0.40;
      fatPercent = 0.35;
  }

  return {
    protein: {
      calories: Math.round(calories * proteinPercent),
      grams: Math.round((calories * proteinPercent) / 4)
    },
    carbs: {
      calories: Math.round(calories * carbPercent),
      grams: Math.round((calories * carbPercent) / 4)
    },
    fat: {
      calories: Math.round(calories * fatPercent),
      grams: Math.round((calories * fatPercent) / 9)
    }
  };
};

// Função para calcular ingestão de água recomendada
export const calculateWaterIntake = (weight, activityLevel) => {
  let baseWater = weight * 35; // 35ml por kg de peso corporal
  
  // Ajustar baseado no nível de atividade
  const activityMultipliers = {
    sedentary: 1.0,
    light: 1.1,
    moderate: 1.2,
    very_active: 1.3,
    extremely_active: 1.4
  };
  
  return Math.round(baseWater * (activityMultipliers[activityLevel] || 1.0));
};

// Função para calcular proteína por kg de peso corporal
export const calculateProteinPerKg = (goal, activityLevel) => {
  let baseProtein = 0.8; // Recomendação mínima
  
  switch (goal) {
    case 'weight_loss':
      baseProtein = activityLevel === 'very_active' || activityLevel === 'extremely_active' ? 2.2 : 1.8;
      break;
    case 'muscle_gain':
      baseProtein = 2.0;
      break;
    case 'maintenance':
      baseProtein = activityLevel === 'very_active' || activityLevel === 'extremely_active' ? 1.6 : 1.2;
      break;
    case 'performance':
      baseProtein = 2.2;
      break;
  }
  
  return baseProtein;
};

