// ANAMNESE ORIGINAL DO PROJETO EVOLVEYOU - 22 PERGUNTAS INTELIGENTES
// Importando da anamnese original
import { anamneseOriginal, calculateAdjustedBMR, calculateTDEE as calcTDEE } from './anamneseOriginal.js';

export const anamneseQuestions = anamneseOriginal;

// Funções de cálculo para compatibilidade com componentes existentes
export const calculateBMR = (weight, height, age, gender) => {
  if (gender === 'male' || gender === 'Masculino') {
    return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
  } else {
    return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
  }
};

export const calculateTDEE = (bmr, activityLevel) => {
  const multipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    very_active: 1.725,
    extremely_active: 1.9,
    'sedentario': 1.2,
    'leve': 1.375,
    'moderado': 1.55,
    'intenso': 1.725
  };
  
  return bmr * (multipliers[activityLevel] || 1.2);
};

export const calculateBMI = (weight, height) => {
  const heightInMeters = height / 100;
  return weight / (heightInMeters * heightInMeters);
};

export const classifyBMI = (bmi) => {
  if (bmi < 18.5) return { category: 'Abaixo do peso', color: 'text-blue-500' };
  if (bmi < 25) return { category: 'Peso normal', color: 'text-green-500' };
  if (bmi < 30) return { category: 'Sobrepeso', color: 'text-yellow-500' };
  return { category: 'Obesidade', color: 'text-red-500' };
};

export const calculateMacros = (calories, goal) => {
  let proteinPercent, carbPercent, fatPercent;
  
  switch (goal) {
    case 'weight_loss':
    case 'emagrecer':
      proteinPercent = 0.30;
      carbPercent = 0.35;
      fatPercent = 0.35;
      break;
    case 'muscle_gain':
    case 'ganhar_massa':
      proteinPercent = 0.25;
      carbPercent = 0.45;
      fatPercent = 0.30;
      break;
    case 'maintenance':
    case 'manter_peso':
      proteinPercent = 0.25;
      carbPercent = 0.40;
      fatPercent = 0.35;
      break;
    case 'performance':
    case 'melhorar_saude':
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

