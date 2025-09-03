// Base de Dados TACO (Tabela Brasileira de Composição de Alimentos)
// Implementação completa com alimentos brasileiros e informações nutricionais precisas

export const tacoDatabase = [
  // CEREAIS E DERIVADOS
  {
    id: "001",
    nome: "Arroz, integral, cozido",
    categoria: "cereais_derivados",
    grupo: "cereais",
    energia_kcal: 124,
    proteina_g: 2.6,
    lipidios_g: 1.0,
    carboidrato_g: 25.8,
    fibra_g: 2.7,
    calcio_mg: 5,
    ferro_mg: 0.3,
    magnesio_mg: 59,
    fosforo_mg: 106,
    potassio_mg: 75,
    sodio_mg: 1,
    zinco_mg: 0.7,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 25 },
      { nome: "xícara", peso_g: 150 },
      { nome: "prato raso", peso_g: 125 }
    ]
  },
  {
    id: "002",
    nome: "Arroz, branco, cozido",
    categoria: "cereais_derivados",
    grupo: "cereais",
    energia_kcal: 128,
    proteina_g: 2.5,
    lipidios_g: 0.2,
    carboidrato_g: 28.1,
    fibra_g: 1.6,
    calcio_mg: 4,
    ferro_mg: 0.1,
    magnesio_mg: 3,
    fosforo_mg: 21,
    potassio_mg: 16,
    sodio_mg: 1,
    zinco_mg: 0.2,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 25 },
      { nome: "xícara", peso_g: 150 },
      { nome: "prato raso", peso_g: 125 }
    ]
  },
  {
    id: "003",
    nome: "Aveia, flocos",
    categoria: "cereais_derivados",
    grupo: "cereais",
    energia_kcal: 394,
    proteina_g: 13.9,
    lipidios_g: 8.5,
    carboidrato_g: 67.0,
    fibra_g: 9.1,
    calcio_mg: 48,
    ferro_mg: 4.4,
    magnesio_mg: 119,
    fosforo_mg: 153,
    potassio_mg: 336,
    sodio_mg: 5,
    zinco_mg: 2.3,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 10 },
      { nome: "xícara", peso_g: 80 }
    ]
  },
  {
    id: "004",
    nome: "Pão francês",
    categoria: "cereais_derivados",
    grupo: "paes",
    energia_kcal: 300,
    proteina_g: 9.4,
    lipidios_g: 3.1,
    carboidrato_g: 58.6,
    fibra_g: 6.5,
    calcio_mg: 40,
    ferro_mg: 2.3,
    magnesio_mg: 22,
    fosforo_mg: 72,
    potassio_mg: 88,
    sodio_mg: 643,
    zinco_mg: 0.6,
    porcao_padrao: 50,
    medidas_caseiras: [
      { nome: "unidade", peso_g: 50 },
      { nome: "fatia", peso_g: 25 }
    ]
  },
  {
    id: "005",
    nome: "Pão integral",
    categoria: "cereais_derivados",
    grupo: "paes",
    energia_kcal: 253,
    proteina_g: 9.7,
    lipidios_g: 3.5,
    carboidrato_g: 48.7,
    fibra_g: 6.9,
    calcio_mg: 57,
    ferro_mg: 2.8,
    magnesio_mg: 53,
    fosforo_mg: 115,
    potassio_mg: 177,
    sodio_mg: 489,
    zinco_mg: 1.1,
    porcao_padrao: 50,
    medidas_caseiras: [
      { nome: "fatia", peso_g: 25 },
      { nome: "unidade pequena", peso_g: 50 }
    ]
  },

  // CARNES E DERIVADOS
  {
    id: "101",
    nome: "Frango, peito, sem pele, grelhado",
    categoria: "carnes_derivados",
    grupo: "aves",
    energia_kcal: 159,
    proteina_g: 32.0,
    lipidios_g: 2.5,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 2,
    ferro_mg: 0.4,
    magnesio_mg: 22,
    fosforo_mg: 174,
    potassio_mg: 216,
    sodio_mg: 47,
    zinco_mg: 0.7,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "filé médio", peso_g: 120 },
      { nome: "fatia", peso_g: 30 }
    ]
  },
  {
    id: "102",
    nome: "Carne bovina, alcatra, assada",
    categoria: "carnes_derivados",
    grupo: "bovinos",
    energia_kcal: 163,
    proteina_g: 30.7,
    lipidios_g: 4.0,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 4,
    ferro_mg: 2.8,
    magnesio_mg: 22,
    fosforo_mg: 175,
    potassio_mg: 327,
    sodio_mg: 45,
    zinco_mg: 5.2,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "bife médio", peso_g: 100 },
      { nome: "fatia", peso_g: 30 }
    ]
  },
  {
    id: "103",
    nome: "Peixe, salmão, grelhado",
    categoria: "carnes_derivados",
    grupo: "peixes",
    energia_kcal: 192,
    proteina_g: 29.2,
    lipidios_g: 7.7,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 59,
    ferro_mg: 0.3,
    magnesio_mg: 30,
    fosforo_mg: 371,
    potassio_mg: 628,
    sodio_mg: 59,
    zinco_mg: 0.6,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "filé médio", peso_g: 120 },
      { nome: "posta", peso_g: 150 }
    ]
  },
  {
    id: "104",
    nome: "Ovo, galinha, inteiro, cozido",
    categoria: "carnes_derivados",
    grupo: "ovos",
    energia_kcal: 155,
    proteina_g: 13.3,
    lipidios_g: 10.6,
    carboidrato_g: 0.6,
    fibra_g: 0.0,
    calcio_mg: 54,
    ferro_mg: 1.9,
    magnesio_mg: 12,
    fosforo_mg: 172,
    potassio_mg: 154,
    sodio_mg: 140,
    zinco_mg: 1.1,
    porcao_padrao: 50,
    medidas_caseiras: [
      { nome: "unidade", peso_g: 50 },
      { nome: "unidade grande", peso_g: 60 }
    ]
  },

  // LEITES E DERIVADOS
  {
    id: "201",
    nome: "Leite, vaca, integral",
    categoria: "leites_derivados",
    grupo: "leites",
    energia_kcal: 61,
    proteina_g: 2.9,
    lipidios_g: 3.2,
    carboidrato_g: 4.3,
    fibra_g: 0.0,
    calcio_mg: 113,
    ferro_mg: 0.1,
    magnesio_mg: 10,
    fosforo_mg: 84,
    potassio_mg: 140,
    sodio_mg: 4,
    zinco_mg: 0.4,
    porcao_padrao: 200,
    medidas_caseiras: [
      { nome: "copo", peso_g: 200 },
      { nome: "xícara", peso_g: 150 }
    ]
  },
  {
    id: "202",
    nome: "Iogurte, natural, integral",
    categoria: "leites_derivados",
    grupo: "iogurtes",
    energia_kcal: 51,
    proteina_g: 4.1,
    lipidios_g: 1.5,
    carboidrato_g: 6.0,
    fibra_g: 0.0,
    calcio_mg: 143,
    ferro_mg: 0.1,
    magnesio_mg: 11,
    fosforo_mg: 95,
    potassio_mg: 141,
    sodio_mg: 44,
    zinco_mg: 0.4,
    porcao_padrao: 170,
    medidas_caseiras: [
      { nome: "pote", peso_g: 170 },
      { nome: "copo", peso_g: 200 }
    ]
  },
  {
    id: "203",
    nome: "Queijo, mussarela",
    categoria: "leites_derivados",
    grupo: "queijos",
    energia_kcal: 289,
    proteina_g: 20.3,
    lipidios_g: 22.4,
    carboidrato_g: 1.0,
    fibra_g: 0.0,
    calcio_mg: 875,
    ferro_mg: 0.2,
    magnesio_mg: 19,
    fosforo_mg: 354,
    potassio_mg: 76,
    sodio_mg: 643,
    zinco_mg: 2.8,
    porcao_padrao: 30,
    medidas_caseiras: [
      { nome: "fatia", peso_g: 15 },
      { nome: "fatia média", peso_g: 30 }
    ]
  },

  // LEGUMINOSAS
  {
    id: "301",
    nome: "Feijão, carioca, cozido",
    categoria: "leguminosas",
    grupo: "feijoes",
    energia_kcal: 76,
    proteina_g: 4.8,
    lipidios_g: 0.5,
    carboidrato_g: 13.6,
    fibra_g: 8.5,
    calcio_mg: 27,
    ferro_mg: 1.3,
    magnesio_mg: 40,
    fosforo_mg: 88,
    potassio_mg: 256,
    sodio_mg: 2,
    zinco_mg: 0.7,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "concha", peso_g: 80 },
      { nome: "colher de sopa", peso_g: 20 }
    ]
  },
  {
    id: "302",
    nome: "Lentilha, cozida",
    categoria: "leguminosas",
    grupo: "lentilhas",
    energia_kcal: 93,
    proteina_g: 6.3,
    lipidios_g: 0.1,
    carboidrato_g: 16.3,
    fibra_g: 7.9,
    calcio_mg: 17,
    ferro_mg: 1.5,
    magnesio_mg: 36,
    fosforo_mg: 99,
    potassio_mg: 284,
    sodio_mg: 2,
    zinco_mg: 1.0,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "concha", peso_g: 80 },
      { nome: "colher de sopa", peso_g: 20 }
    ]
  },

  // VERDURAS E LEGUMES
  {
    id: "401",
    nome: "Brócolis, cozido",
    categoria: "verduras_legumes",
    grupo: "verduras",
    energia_kcal: 25,
    proteina_g: 3.6,
    lipidios_g: 0.4,
    carboidrato_g: 4.0,
    fibra_g: 3.4,
    calcio_mg: 86,
    ferro_mg: 0.5,
    magnesio_mg: 24,
    fosforo_mg: 78,
    potassio_mg: 325,
    sodio_mg: 8,
    zinco_mg: 0.4,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "ramo médio", peso_g: 30 },
      { nome: "colher de sopa", peso_g: 15 }
    ]
  },
  {
    id: "402",
    nome: "Cenoura, crua",
    categoria: "verduras_legumes",
    grupo: "legumes",
    energia_kcal: 34,
    proteina_g: 1.3,
    lipidios_g: 0.2,
    carboidrato_g: 7.7,
    fibra_g: 3.2,
    calcio_mg: 27,
    ferro_mg: 0.6,
    magnesio_mg: 12,
    fosforo_mg: 32,
    potassio_mg: 323,
    sodio_mg: 65,
    zinco_mg: 0.2,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "unidade média", peso_g: 110 },
      { nome: "fatia", peso_g: 15 }
    ]
  },
  {
    id: "403",
    nome: "Tomate, cru",
    categoria: "verduras_legumes",
    grupo: "legumes",
    energia_kcal: 15,
    proteina_g: 1.1,
    lipidios_g: 0.2,
    carboidrato_g: 3.1,
    fibra_g: 1.2,
    calcio_mg: 9,
    ferro_mg: 0.3,
    magnesio_mg: 9,
    fosforo_mg: 21,
    potassio_mg: 222,
    sodio_mg: 4,
    zinco_mg: 0.1,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "unidade média", peso_g: 120 },
      { nome: "fatia", peso_g: 15 }
    ]
  },

  // FRUTAS
  {
    id: "501",
    nome: "Banana, nanica",
    categoria: "frutas",
    grupo: "frutas_tropicais",
    energia_kcal: 92,
    proteina_g: 1.3,
    lipidios_g: 0.1,
    carboidrato_g: 23.8,
    fibra_g: 2.0,
    calcio_mg: 8,
    ferro_mg: 0.4,
    magnesio_mg: 28,
    fosforo_mg: 20,
    potassio_mg: 376,
    sodio_mg: 2,
    zinco_mg: 0.2,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "unidade", peso_g: 86 },
      { nome: "unidade pequena", peso_g: 65 }
    ]
  },
  {
    id: "502",
    nome: "Maçã, com casca",
    categoria: "frutas",
    grupo: "frutas_temperadas",
    energia_kcal: 56,
    proteina_g: 0.3,
    lipidios_g: 0.1,
    carboidrato_g: 15.2,
    fibra_g: 1.3,
    calcio_mg: 3,
    ferro_mg: 0.1,
    magnesio_mg: 2,
    fosforo_mg: 9,
    potassio_mg: 117,
    sodio_mg: 2,
    zinco_mg: 0.0,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "unidade média", peso_g: 130 },
      { nome: "fatia", peso_g: 15 }
    ]
  },
  {
    id: "503",
    nome: "Laranja, pera",
    categoria: "frutas",
    grupo: "citricos",
    energia_kcal: 37,
    proteina_g: 0.9,
    lipidios_g: 0.1,
    carboidrato_g: 9.1,
    fibra_g: 1.7,
    calcio_mg: 4,
    ferro_mg: 0.1,
    magnesio_mg: 9,
    fosforo_mg: 17,
    potassio_mg: 163,
    sodio_mg: 7,
    zinco_mg: 0.1,
    porcao_padrao: 100,
    medidas_caseiras: [
      { nome: "unidade média", peso_g: 180 },
      { nome: "gomo", peso_g: 15 }
    ]
  },

  // ÓLEOS E GORDURAS
  {
    id: "601",
    nome: "Azeite de oliva",
    categoria: "oleos_gorduras",
    grupo: "oleos_vegetais",
    energia_kcal: 884,
    proteina_g: 0.0,
    lipidios_g: 100.0,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 1,
    ferro_mg: 0.6,
    magnesio_mg: 0,
    fosforo_mg: 0,
    potassio_mg: 1,
    sodio_mg: 2,
    zinco_mg: 0.0,
    porcao_padrao: 10,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 8 },
      { nome: "colher de chá", peso_g: 3 }
    ]
  },
  {
    id: "602",
    nome: "Óleo de soja",
    categoria: "oleos_gorduras",
    grupo: "oleos_vegetais",
    energia_kcal: 884,
    proteina_g: 0.0,
    lipidios_g: 100.0,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 0,
    ferro_mg: 0.0,
    magnesio_mg: 0,
    fosforo_mg: 0,
    potassio_mg: 0,
    sodio_mg: 0,
    zinco_mg: 0.0,
    porcao_padrao: 10,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 8 },
      { nome: "colher de chá", peso_g: 3 }
    ]
  },

  // AÇÚCARES E DOCES
  {
    id: "701",
    nome: "Açúcar, cristal",
    categoria: "acucares_doces",
    grupo: "acucares",
    energia_kcal: 387,
    proteina_g: 0.0,
    lipidios_g: 0.0,
    carboidrato_g: 99.5,
    fibra_g: 0.0,
    calcio_mg: 1,
    ferro_mg: 0.1,
    magnesio_mg: 0,
    fosforo_mg: 0,
    potassio_mg: 2,
    sodio_mg: 1,
    zinco_mg: 0.0,
    porcao_padrao: 10,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 12 },
      { nome: "colher de chá", peso_g: 4 }
    ]
  },
  {
    id: "702",
    nome: "Mel",
    categoria: "acucares_doces",
    grupo: "adocantes_naturais",
    energia_kcal: 309,
    proteina_g: 0.4,
    lipidios_g: 0.0,
    carboidrato_g: 84.0,
    fibra_g: 0.0,
    calcio_mg: 5,
    ferro_mg: 0.4,
    magnesio_mg: 1,
    fosforo_mg: 5,
    potassio_mg: 47,
    sodio_mg: 6,
    zinco_mg: 0.1,
    porcao_padrao: 20,
    medidas_caseiras: [
      { nome: "colher de sopa", peso_g: 20 },
      { nome: "colher de chá", peso_g: 7 }
    ]
  },

  // BEBIDAS
  {
    id: "801",
    nome: "Água",
    categoria: "bebidas",
    grupo: "agua",
    energia_kcal: 0,
    proteina_g: 0.0,
    lipidios_g: 0.0,
    carboidrato_g: 0.0,
    fibra_g: 0.0,
    calcio_mg: 0,
    ferro_mg: 0.0,
    magnesio_mg: 0,
    fosforo_mg: 0,
    potassio_mg: 0,
    sodio_mg: 0,
    zinco_mg: 0.0,
    porcao_padrao: 200,
    medidas_caseiras: [
      { nome: "copo", peso_g: 200 },
      { nome: "garrafa 500ml", peso_g: 500 }
    ]
  }
];

// Funções utilitárias para busca e filtros
export const searchFoods = (query) => {
  if (!query) return tacoDatabase;
  
  const searchTerm = query.toLowerCase();
  return tacoDatabase.filter(food => 
    food.nome.toLowerCase().includes(searchTerm) ||
    food.categoria.toLowerCase().includes(searchTerm) ||
    food.grupo.toLowerCase().includes(searchTerm)
  );
};

export const getFoodsByCategory = (category) => {
  return tacoDatabase.filter(food => food.categoria === category);
};

export const getFoodById = (id) => {
  return tacoDatabase.find(food => food.id === id);
};

export const calculateNutrition = (foodId, quantity) => {
  const food = getFoodById(foodId);
  if (!food) return null;
  
  const factor = quantity / 100; // TACO é baseado em 100g
  
  return {
    ...food,
    quantidade_g: quantity,
    energia_kcal: Math.round(food.energia_kcal * factor),
    proteina_g: Math.round(food.proteina_g * factor * 10) / 10,
    lipidios_g: Math.round(food.lipidios_g * factor * 10) / 10,
    carboidrato_g: Math.round(food.carboidrato_g * factor * 10) / 10,
    fibra_g: Math.round(food.fibra_g * factor * 10) / 10
  };
};

// Categorias disponíveis
export const foodCategories = [
  { id: "cereais_derivados", nome: "Cereais e Derivados", icon: "🌾" },
  { id: "carnes_derivados", nome: "Carnes e Derivados", icon: "🥩" },
  { id: "leites_derivados", nome: "Leites e Derivados", icon: "🥛" },
  { id: "leguminosas", nome: "Leguminosas", icon: "🫘" },
  { id: "verduras_legumes", nome: "Verduras e Legumes", icon: "🥬" },
  { id: "frutas", nome: "Frutas", icon: "🍎" },
  { id: "oleos_gorduras", nome: "Óleos e Gorduras", icon: "🫒" },
  { id: "acucares_doces", nome: "Açúcares e Doces", icon: "🍯" },
  { id: "bebidas", nome: "Bebidas", icon: "💧" }
];

export default tacoDatabase;

