// ANAMNESE ORIGINAL DO PROJETO EVOLVEYOU
// Baseada no documento ProjetoEvolveYouv1.docx

export const anamneseOriginal = [
  // PARTE 1: O PONTO DE PARTIDA
  {
    id: 1,
    section: "O PONTO DE PARTIDA",
    question: "Qual é o seu principal objetivo neste momento?",
    type: "single_choice",
    required: true,
    options: [
      { value: "emagrecer", label: "Emagrecer e perder gordura corporal (preservar massa muscular)" },
      { value: "ganhar_massa", label: "Ganhar massa muscular (hipertrofia)" },
      { value: "melhorar_saude", label: "Melhorar minha saúde e condicionamento físico geral (performance)" },
      { value: "manter_peso", label: "Manter meu peso e composição corporal atuais (manutenção)" },
      { value: "reabilitacao", label: "Reabilitação, melhora postural" }
    ]
  },
  {
    id: 2,
    section: "O PONTO DE PARTIDA",
    question: "Qual é a principal MOTIVAÇÃO por trás do seu objetivo? (Marque as principais)",
    type: "multiple_choice",
    required: true,
    options: [
      { value: "saude", label: "Melhorar minha saúde e bem-estar geral" },
      { value: "autoestima", label: "Aumentar minha autoestima e me sentir mais confiante" },
      { value: "evento", label: "Tenho um evento específico (viagem, casamento, formatura)" },
      { value: "competicao", label: "Performance para uma competição ou prova esportiva" },
      { value: "avaliacao", label: "Preparação para uma avaliação física (concurso, teste de emprego)" },
      { value: "outro", label: "Outro motivo", hasInput: true }
    ]
  },
  {
    id: 3,
    section: "O PONTO DE PARTIDA",
    question: "Em quanto tempo você pretende alcançar este objetivo?",
    type: "single_choice",
    required: true,
    options: [
      { value: "curto", label: "Curto Prazo: O mais rápido possível" },
      { value: "medio", label: "Médio Prazo: Tenho um bom tempo" },
      { value: "longo", label: "Longo Prazo: Sem pressa, focando na consistência" },
      { value: "continuo", label: "Contínuo: É um projeto de estilo de vida, sem um prazo final" }
    ]
  },
  {
    id: 4,
    section: "O PONTO DE PARTIDA",
    question: "Para refinar, qual destas frases melhor descreve sua mentalidade?",
    type: "single_choice",
    required: true,
    options: [
      { value: "agressiva", label: "Prefiro uma abordagem mais agressiva, mesmo que seja mais difícil" },
      { value: "sustentavel", label: "Prefiro uma abordagem mais lenta e sustentável, que se encaixe melhor na minha rotina" }
    ]
  },
  {
    id: 5,
    section: "DADOS BÁSICOS",
    question: "Seus dados básicos:",
    type: "personal_data",
    required: true,
    fields: [
      { name: "sexo", label: "Sexo Biológico", type: "select", options: ["Masculino", "Feminino"] },
      { name: "idade", label: "Idade", type: "number", placeholder: "anos" },
      { name: "altura", label: "Altura", type: "number", placeholder: "cm" },
      { name: "peso", label: "Peso", type: "number", placeholder: "kg" }
    ]
  },

  // PARTE 2: SUA ROTINA E METABOLISMO
  {
    id: 6,
    section: "SUA ROTINA E METABOLISMO",
    question: "Como você descreveria seu corpo hoje, olhando no espelho?",
    type: "single_choice",
    required: true,
    options: [
      { value: "muito_magro", label: "Muito magro(a), com ossos e músculos bem visíveis" },
      { value: "magro", label: "Magro(a), com pouca gordura aparente e um visual 'seco'" },
      { value: "atletico", label: "Atlético(a), com músculos definidos e pouca gordura" },
      { value: "normal", label: "Normal ou mediano, com um pouco de gordura cobrindo os músculos" },
      { value: "acima_peso", label: "Acima do peso, com acúmulo de gordura notável na barriga, quadris ou outras áreas" }
    ]
  },
  {
    id: 7,
    section: "SUA ROTINA E METABOLISMO",
    question: "Qual opção melhor descreve sua principal atividade no TRABALHO ou ESTUDOS?",
    type: "single_choice",
    required: true,
    options: [
      { value: "sedentario", label: "Nível 1 - Sedentário: Passo a maior parte do tempo sentado(a) (ex: escritório, motorista)" },
      { value: "leve", label: "Nível 2 - Leve: Fico parte do tempo sentado(a), mas caminho um pouco ou fico em pé (ex: professor, vendedor)" },
      { value: "moderado", label: "Nível 3 - Moderado: Estou em constante movimento, caminhando bastante (ex: garçom, estoquista)" },
      { value: "intenso", label: "Nível 4 - Intenso: Meu trabalho exige muito esforço físico e carregar pesos (ex: construção civil)" }
    ]
  },
  {
    id: 8,
    section: "SUA ROTINA E METABOLISMO",
    question: "E no seu TEMPO LIVRE (fora do trabalho e dos treinos), você se considera uma pessoa:",
    type: "single_choice",
    required: true,
    options: [
      { value: "tranquila", label: "Nível 1 - Muito tranquila: Passo a maior parte do tempo em atividades de baixo esforço (ler, ver TV)" },
      { value: "leve_ativa", label: "Nível 2 - Levemente ativa: Faço tarefas domésticas leves e pequenas caminhadas" },
      { value: "ativa", label: "Nível 3 - Ativa: Estou sempre fazendo algo, como limpeza pesada, jardinagem, passeios longos" }
    ]
  },

  // PARTE 3: SEU HISTÓRICO, TREINO E PERFORMANCE
  {
    id: 9,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Qual seu nível de experiência com treinos de força (musculação, Crossfit)?",
    type: "single_choice",
    required: true,
    options: [
      { value: "iniciante", label: "Iniciante: Nunca treinei ou treinei por menos de 6 meses" },
      { value: "intermediario", label: "Intermediário: Treino de forma consistente há mais de 6 meses a 2 anos" },
      { value: "avancado", label: "Avançado: Treino de forma séria e consistente há vários anos" }
    ]
  },
  {
    id: 10,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Onde você pretende treinar?",
    type: "single_choice",
    required: true,
    options: [
      { value: "casa_sem_equip", label: "Em casa, com pouco ou nenhum equipamento" },
      { value: "casa_com_equip", label: "Em casa, com alguns equipamentos (halteres, elásticos)" },
      { value: "academia_basica", label: "Em uma academia com equipamentos básicos" },
      { value: "academia_completa", label: "Em uma academia completa" },
      { value: "crossfit", label: "Em um Box de Crossfit" }
    ]
  },
  {
    id: 11,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Quantos dias na semana você REALMENTE tem disponibilidade para treinar?",
    type: "single_choice",
    required: true,
    options: [
      { value: "2", label: "2 dias" },
      { value: "3", label: "3 dias" },
      { value: "4", label: "4 dias" },
      { value: "5", label: "5 dias" },
      { value: "6", label: "6 dias" }
    ]
  },
  {
    id: 12,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Qual(is) atividade(s) você pratica ou gostaria de praticar? (Marque as principais)",
    type: "multiple_choice",
    required: true,
    options: [
      { value: "musculacao", label: "Musculação / Treinamento de Força" },
      { value: "crossfit", label: "Crossfit / Treinamento Funcional" },
      { value: "corrida", label: "Corrida / Caminhada" },
      { value: "esportes_coletivos", label: "Futebol / Vôlei / Basquete" },
      { value: "raquete", label: "Beach Tennis / Tênis / Padel" },
      { value: "ciclismo", label: "Ciclismo / Bike" },
      { value: "natacao", label: "Natação / Hidroginástica" },
      { value: "lutas", label: "Lutas (Jiu-Jitsu, Boxe, etc.)" },
      { value: "danca_yoga", label: "Dança / Yoga / Pilates" },
      { value: "outra", label: "Outra", hasInput: true }
    ]
  },
  {
    id: 13,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Em uma escala de 0 a 10, qual a intensidade média do seu esforço nos treinos?",
    type: "single_choice",
    required: true,
    options: [
      { value: "3-4", label: "3-4 (Leve): Consigo conversar normalmente" },
      { value: "5-6", label: "5-6 (Moderado): Conversar se torna um desafio" },
      { value: "7-8", label: "7-8 (Intenso): Só consigo falar frases curtas" },
      { value: "9-10", label: "9-10 (Muito Intenso): Falar é quase impossível, esforço máximo" }
    ]
  },
  {
    id: 14,
    section: "SEU HISTÓRICO, TREINO E PERFORMANCE",
    question: "Você sente alguma dor, desconforto ou tem alguma lesão ativa ou recorrente?",
    type: "text_with_option",
    required: true,
    options: [
      { value: "nao", label: "Não" },
      { value: "sim", label: "Sim. Descreva:", hasInput: true }
    ]
  },

  // PARTE 4: SUPLEMENTAÇÃO E RECURSOS ERGOGÊNICOS
  {
    id: 15,
    section: "SUPLEMENTAÇÃO E RECURSOS ERGOGÊNICOS",
    question: "Você faz uso ou pretende fazer uso de suplementos alimentares?",
    type: "single_choice",
    required: true,
    options: [
      { value: "nao", label: "Não" },
      { value: "sim", label: "Sim" }
    ]
  },
  {
    id: 16,
    section: "SUPLEMENTAÇÃO E RECURSOS ERGOGÊNICOS",
    question: "Se sim, quais você utiliza ou tem interesse? (Marque todos que se aplicam)",
    type: "multiple_choice",
    required: false,
    conditional: { questionId: 15, value: "sim" },
    categories: [
      {
        name: "MACRONUTRIENTES (para complementar a dieta)",
        options: [
          { value: "proteina_po", label: "Proteína em Pó (Whey Protein, Caseína, Albumina, Proteína Vegana)" },
          { value: "hipercalorico", label: "Hipercalórico / Massa" },
          { value: "carboidratos_po", label: "Carboidratos em Pó (Maltodextrina, Dextrose, Waxy Maize)" }
        ]
      },
      {
        name: "PERFORMANCE E FORÇA",
        options: [
          { value: "creatina", label: "Creatina" },
          { value: "beta_alanina", label: "Beta-Alanina" },
          { value: "cafeina", label: "Cafeína (cápsulas ou como pré-treino)" },
          { value: "citrulina", label: "Citrulina / Arginina" }
        ]
      },
      {
        name: "SAÚDE E BEM-ESTAR (micronutrientes e outros)",
        options: [
          { value: "multivitaminico", label: "Multivitamínico" },
          { value: "vitamina_d", label: "Vitamina D" },
          { value: "omega_3", label: "Ômega 3" },
          { value: "coenzima_q10", label: "Coenzima Q10" },
          { value: "melatonina", label: "Melatonina / Indutores de sono" },
          { value: "outros", label: "Outros", hasInput: true }
        ]
      }
    ]
  },
  {
    id: 17,
    section: "SUPLEMENTAÇÃO E RECURSOS ERGOGÊNICOS",
    question: "Você faz uso de algum recurso ergogênico farmacológico (hormônios/esteroides)?",
    subtitle: "(Esta informação é confidencial e crucial para a segurança e eficácia do seu plano)",
    type: "pharma_usage",
    required: true,
    options: [
      { value: "nao", label: "Não" },
      { value: "sim", label: "Sim" }
    ],
    pharmaFields: [
      { name: "nome", label: "Nome do Recurso", placeholder: "ex: Testosterona" },
      { name: "dosagem", label: "Dosagem", placeholder: "ex: 200mg" },
      { name: "frequencia", label: "Frequência", placeholder: "ex: uma vez por semana" }
    ]
  },

  // PARTE 5: SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES
  {
    id: 18,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Quantas refeições você costuma fazer por dia?",
    type: "single_choice",
    required: true,
    options: [
      { value: "1-2", label: "1 a 2 refeições grandes" },
      { value: "3", label: "3 refeições principais (café, almoço, jantar)" },
      { value: "4-5", label: "4 a 5 refeições (as 3 principais + lanches)" },
      { value: "6+", label: "6 ou mais refeições pequenas ao longo do dia" }
    ]
  },
  {
    id: 19,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Marque as fontes de PROTEÍNA que você mais gosta e costuma comer:",
    type: "multiple_choice",
    required: true,
    options: [
      { value: "frango", label: "Frango" },
      { value: "carne_vermelha", label: "Carne vermelha (bovina, suína)" },
      { value: "peixes", label: "Peixes (tilápia, salmão)" },
      { value: "ovos", label: "Ovos" },
      { value: "laticinios", label: "Laticínios (iogurte, queijos)" },
      { value: "proteinas_po", label: "Proteínas em pó (Whey, Albumina)" },
      { value: "proteinas_vegetais", label: "Proteínas vegetais (lentilha, grão-de-bico, tofu, soja)" }
    ]
  },
  {
    id: 20,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Marque as fontes de CARBOIDRATO que você mais gosta e costuma comer:",
    type: "multiple_choice",
    required: true,
    options: [
      { value: "arroz", label: "Arroz branco / integral" },
      { value: "batatas", label: "Batatas (inglesa, doce) / Mandioca" },
      { value: "massas", label: "Massas / Pães" },
      { value: "aveia", label: "Aveia" },
      { value: "frutas", label: "Frutas em geral" },
      { value: "legumes", label: "Legumes e verduras" }
    ]
  },
  {
    id: 21,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Você possui alguma alergia, intolerância ou restrição alimentar severa?",
    type: "text_with_option",
    required: true,
    options: [
      { value: "nao", label: "Não" },
      { value: "lactose", label: "Sim, a lactose" },
      { value: "gluten", label: "Sim, ao glúten (Celíaco ou sensibilidade)" },
      { value: "outros", label: "Sim, a outros alimentos. Quais?", hasInput: true }
    ]
  },
  {
    id: 22,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Quanta água você bebe por dia?",
    type: "single_choice",
    required: true,
    options: [
      { value: "quase_nada", label: "Quase não bebo água, mais sucos e refrigerantes" },
      { value: "1-2_copos", label: "1 a 2 copos (menos de 1 litro)" },
      { value: "3-5_copos", label: "3 a 5 copos (cerca de 1,5 litros)" },
      { value: "6+_copos", label: "Mais de 6 copos (mais de 2 litros)" }
    ]
  },
  {
    id: 23,
    section: "SEUS HÁBITOS E PREFERÊNCIAS ALIMENTARES",
    question: "Como é sua alimentação nos fins de semana?",
    type: "single_choice",
    required: true,
    options: [
      { value: "mesmo_padrao", label: "Mantenho o mesmo padrão da semana" },
      { value: "1-2_livres", label: "Faço de 1 a 2 'refeições livres' (pizza, lanche, etc)" },
      { value: "muito_diferente", label: "É bem diferente, com muito mais 'escapadas' da dieta" }
    ]
  }
];

// Fatores de ajuste para cálculos metabólicos (conforme projeto original)
export const metabolicFactors = {
  bodyComposition: {
    muito_magro: 0.95,
    magro: 0.98,
    atletico: 1.08,
    normal: 1.0,
    acima_peso: 1.02
  },
  
  pharmaUsage: {
    nao: 1.0,
    sim: 1.10 // Ajuste base para uso de ergogênicos
  },
  
  experience: {
    iniciante: 1.0,
    intermediario: 1.02,
    avancado: 1.05
  },
  
  workActivity: {
    sedentario: 1.2,
    leve: 1.375,
    moderado: 1.55,
    intenso: 1.725
  },
  
  leisureActivity: {
    tranquila: 0.0,
    leve_ativa: 0.1,
    ativa: 0.2
  }
};

// Função para calcular GMB ajustado (Fórmula EvolveYou)
export const calculateAdjustedBMR = (userData) => {
  const { idade, peso, altura, sexo } = userData.dadosBasicos;
  const { composicaoCorporal, experienciaTreino, usoErgogenicos } = userData;
  
  // GMB base usando Mifflin-St Jeor
  let bmrBase;
  if (sexo === 'Masculino') {
    bmrBase = (10 * peso) + (6.25 * altura) - (5 * idade) + 5;
  } else {
    bmrBase = (10 * peso) + (6.25 * altura) - (5 * idade) - 161;
  }
  
  // Aplicar fatores de ajuste
  const bodyFactor = metabolicFactors.bodyComposition[composicaoCorporal] || 1.0;
  const pharmaFactor = metabolicFactors.pharmaUsage[usoErgogenicos] || 1.0;
  const experienceFactor = metabolicFactors.experience[experienciaTreino] || 1.0;
  
  const adjustedBMR = bmrBase * bodyFactor * pharmaFactor * experienceFactor;
  
  return Math.round(adjustedBMR);
};

// Função para calcular TDEE (Total Daily Energy Expenditure)
export const calculateTDEE = (adjustedBMR, workActivity, leisureActivity) => {
  const workFactor = metabolicFactors.workActivity[workActivity] || 1.375;
  const leisureFactor = metabolicFactors.leisureActivity[leisureActivity] || 0.0;
  
  const tdee = adjustedBMR * (workFactor + leisureFactor);
  
  return Math.round(tdee);
};

