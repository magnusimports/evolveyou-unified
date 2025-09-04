import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, ArrowRight, CheckCircle, Loader2, Plus, Trash2 } from 'lucide-react';
import { useAuth } from '../hooks/useFirebaseAuth.jsx';
import { anamneseOriginal, calculateAdjustedBMR, calculateTDEE as calcTDEE } from '../data/anamneseOriginal.js';

const OnboardingOriginal = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [pharmaList, setPharmaList] = useState([{ nome: '', dosagem: '', frequencia: '' }]);
  
  const { user, updateUserProfile } = useAuth();
  const navigate = useNavigate();

  const totalSteps = anamneseOriginal.length;
  const progress = ((currentStep + 1) / totalSteps) * 100;
  const currentQuestion = anamneseOriginal[currentStep];

  // Verificar se pergunta deve ser mostrada (lógica condicional)
  const shouldShowQuestion = (question) => {
    if (!question.conditional) return true;
    
    const { questionId, value } = question.conditional;
    const previousAnswer = answers[questionId];
    return previousAnswer === value;
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleMultipleChoice = (questionId, optionValue, checked) => {
    setAnswers(prev => {
      const currentAnswers = prev[questionId] || [];
      if (checked) {
        return {
          ...prev,
          [questionId]: [...currentAnswers, optionValue]
        };
      } else {
        return {
          ...prev,
          [questionId]: currentAnswers.filter(item => item !== optionValue)
        };
      }
    });
  };

  const handlePersonalData = (field, value) => {
    setAnswers(prev => ({
      ...prev,
      [`personal_${field}`]: value
    }));
  };

  const handlePharmaChange = (index, field, value) => {
    const newPharmaList = [...pharmaList];
    newPharmaList[index][field] = value;
    setPharmaList(newPharmaList);
    
    setAnswers(prev => ({
      ...prev,
      pharma_details: newPharmaList.filter(item => item.nome.trim() !== '')
    }));
  };

  const addPharmaItem = () => {
    setPharmaList([...pharmaList, { nome: '', dosagem: '', frequencia: '' }]);
  };

  const removePharmaItem = (index) => {
    if (pharmaList.length > 1) {
      const newPharmaList = pharmaList.filter((_, i) => i !== index);
      setPharmaList(newPharmaList);
      
      setAnswers(prev => ({
        ...prev,
        pharma_details: newPharmaList.filter(item => item.nome.trim() !== '')
      }));
    }
  };

  const handleNext = () => {
    // Pular perguntas condicionais que não devem ser mostradas
    let nextStep = currentStep + 1;
    while (nextStep < totalSteps && !shouldShowQuestion(anamneseOriginal[nextStep])) {
      nextStep++;
    }
    
    if (nextStep < totalSteps) {
      setCurrentStep(nextStep);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    // Voltar para pergunta anterior válida
    let prevStep = currentStep - 1;
    while (prevStep >= 0 && !shouldShowQuestion(anamneseOriginal[prevStep])) {
      prevStep--;
    }
    
    if (prevStep >= 0) {
      setCurrentStep(prevStep);
    }
  };

  const calculateResults = () => {
    // Extrair dados pessoais
    const dadosBasicos = {
      idade: parseInt(answers.personal_idade) || 25,
      peso: parseFloat(answers.personal_peso) || 70,
      altura: parseFloat(answers.personal_altura) || 170,
      sexo: answers.personal_sexo || 'Masculino'
    };

    // Calcular GMB ajustado usando algoritmos originais
    const userData = {
      dadosBasicos,
      composicaoCorporal: answers[6] || 'normal', // Pergunta 6: Como você descreveria seu corpo
      experienciaTreino: answers[9] || 'iniciante', // Pergunta 9: Nível de experiência
      usoErgogenicos: answers[17] || 'nao' // Pergunta 17: Uso de ergogênicos
    };

    const adjustedBMR = calculateAdjustedBMR(userData);
    
    // Calcular TDEE
    const workActivity = answers[7] || 'sedentario'; // Pergunta 7: Atividade no trabalho
    const leisureActivity = answers[8] || 'tranquila'; // Pergunta 8: Atividade no tempo livre
    
    const tdee = calcTDEE(adjustedBMR, workActivity, leisureActivity);

    // Calcular IMC
    const imc = dadosBasicos.peso / Math.pow(dadosBasicos.altura / 100, 2);
    
    // Determinar objetivo calórico baseado na meta
    const objetivo = answers[1] || 'manter_peso'; // Pergunta 1: Objetivo principal
    let targetCalories = tdee;
    
    switch (objetivo) {
      case 'emagrecer':
        targetCalories = tdee - 450; // Déficit de 450 kcal conforme projeto
        break;
      case 'ganhar_massa':
        targetCalories = tdee + 300; // Superávit de 300 kcal
        break;
      case 'manter_peso':
        targetCalories = tdee;
        break;
      default:
        targetCalories = tdee;
    }

    // Calcular macronutrientes
    const macros = calculateMacros(targetCalories, objetivo);

    return {
      adjustedBMR,
      tdee,
      targetCalories,
      imc,
      macros,
      dadosBasicos,
      objetivo
    };
  };

  const calculateMacros = (calories, goal) => {
    let proteinPercent, carbPercent, fatPercent;
    
    switch (goal) {
      case 'emagrecer':
        proteinPercent = 0.30;
        carbPercent = 0.35;
        fatPercent = 0.35;
        break;
      case 'ganhar_massa':
        proteinPercent = 0.25;
        carbPercent = 0.45;
        fatPercent = 0.30;
        break;
      case 'manter_peso':
        proteinPercent = 0.25;
        carbPercent = 0.40;
        fatPercent = 0.35;
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

  const handleComplete = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Calcular resultados usando algoritmos originais
      const results = calculateResults();
      
      // Salvar dados no Firestore usando o serviço
      const firestoreService = (await import('../services/firestoreService.js')).default;
      await firestoreService.saveAnamneseResults(user.uid, answers, results);
      
      // Navegar para dashboard
      navigate('/dashboard');
    } catch (err) {
      setError('Erro ao salvar suas informações. Tente novamente.');
      console.error('Erro ao completar onboarding:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderQuestion = () => {
    if (!shouldShowQuestion(currentQuestion)) {
      return null;
    }

    const questionId = currentQuestion.id;
    const currentAnswer = answers[questionId];

    switch (currentQuestion.type) {
      case 'single_choice':
        return (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              {currentQuestion.section && (
                <div className="font-semibold text-blue-600 mb-2">
                  {currentQuestion.section}
                </div>
              )}
            </div>
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            {currentQuestion.subtitle && (
              <p className="text-sm text-gray-600 mb-4">{currentQuestion.subtitle}</p>
            )}
            <div className="space-y-3">
              {currentQuestion.options.map((option) => (
                <div
                  key={option.value}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    currentAnswer === option.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleAnswer(questionId, option.value)}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      currentAnswer === option.value
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {currentAnswer === option.value && (
                        <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                      )}
                    </div>
                    <div>
                      <div className="font-medium">{option.label}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'multiple_choice':
        return (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              {currentQuestion.section && (
                <div className="font-semibold text-blue-600 mb-2">
                  {currentQuestion.section}
                </div>
              )}
            </div>
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            
            {currentQuestion.categories ? (
              // Perguntas com categorias (como suplementos)
              <div className="space-y-6">
                {currentQuestion.categories.map((category) => (
                  <div key={category.name} className="space-y-3">
                    <h3 className="font-semibold text-gray-800">{category.name}</h3>
                    <div className="space-y-2 ml-4">
                      {category.options.map((option) => (
                        <div key={option.value} className="flex items-center space-x-3">
                          <Checkbox
                            id={option.value}
                            checked={(currentAnswer || []).includes(option.value)}
                            onCheckedChange={(checked) => 
                              handleMultipleChoice(questionId, option.value, checked)
                            }
                          />
                          <Label htmlFor={option.value} className="text-sm">
                            {option.label}
                          </Label>
                          {option.hasInput && (currentAnswer || []).includes(option.value) && (
                            <Input
                              placeholder="Especifique..."
                              className="ml-4 max-w-xs"
                              onChange={(e) => handleAnswer(`${questionId}_${option.value}_input`, e.target.value)}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              // Perguntas simples de múltipla escolha
              <div className="space-y-3">
                {currentQuestion.options.map((option) => (
                  <div key={option.value} className="flex items-center space-x-3">
                    <Checkbox
                      id={option.value}
                      checked={(currentAnswer || []).includes(option.value)}
                      onCheckedChange={(checked) => 
                        handleMultipleChoice(questionId, option.value, checked)
                      }
                    />
                    <Label htmlFor={option.value} className="text-sm">
                      {option.label}
                    </Label>
                    {option.hasInput && (currentAnswer || []).includes(option.value) && (
                      <Input
                        placeholder="Especifique..."
                        className="ml-4 max-w-xs"
                        onChange={(e) => handleAnswer(`${questionId}_${option.value}_input`, e.target.value)}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'personal_data':
        return (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              <div className="font-semibold text-blue-600 mb-2">
                {currentQuestion.section}
              </div>
            </div>
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentQuestion.fields.map((field) => (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={field.name}>{field.label}</Label>
                  {field.type === 'select' ? (
                    <Select
                      value={answers[`personal_${field.name}`] || ''}
                      onValueChange={(value) => handlePersonalData(field.name, value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={`Selecione ${field.label.toLowerCase()}`} />
                      </SelectTrigger>
                      <SelectContent>
                        {field.options.map((option) => (
                          <SelectItem key={option} value={option}>
                            {option}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      id={field.name}
                      type={field.type}
                      placeholder={field.placeholder}
                      value={answers[`personal_${field.name}`] || ''}
                      onChange={(e) => handlePersonalData(field.name, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      case 'pharma_usage':
        return (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              <div className="font-semibold text-blue-600 mb-2">
                {currentQuestion.section}
              </div>
            </div>
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            {currentQuestion.subtitle && (
              <p className="text-sm text-gray-600 mb-4 italic">{currentQuestion.subtitle}</p>
            )}
            
            <div className="space-y-3">
              {currentQuestion.options.map((option) => (
                <div
                  key={option.value}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    currentAnswer === option.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleAnswer(questionId, option.value)}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      currentAnswer === option.value
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {currentAnswer === option.value && (
                        <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                      )}
                    </div>
                    <div className="font-medium">{option.label}</div>
                  </div>
                </div>
              ))}
            </div>

            {currentAnswer === 'sim' && (
              <div className="mt-6 space-y-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800">Detalhes dos recursos utilizados:</h3>
                {pharmaList.map((item, index) => (
                  <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                    <div>
                      <Label>Nome do Recurso</Label>
                      <Input
                        placeholder="ex: Testosterona"
                        value={item.nome}
                        onChange={(e) => handlePharmaChange(index, 'nome', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label>Dosagem</Label>
                      <Input
                        placeholder="ex: 200mg"
                        value={item.dosagem}
                        onChange={(e) => handlePharmaChange(index, 'dosagem', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label>Frequência</Label>
                      <Input
                        placeholder="ex: uma vez por semana"
                        value={item.frequencia}
                        onChange={(e) => handlePharmaChange(index, 'frequencia', e.target.value)}
                      />
                    </div>
                    <div className="flex space-x-2">
                      {index === pharmaList.length - 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={addPharmaItem}
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                      )}
                      {pharmaList.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removePharmaItem(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'text_with_option':
        return (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              <div className="font-semibold text-blue-600 mb-2">
                {currentQuestion.section}
              </div>
            </div>
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            <div className="space-y-3">
              {currentQuestion.options.map((option) => (
                <div key={option.value} className="space-y-3">
                  <div
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      currentAnswer === option.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleAnswer(questionId, option.value)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        currentAnswer === option.value
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                      }`}>
                        {currentAnswer === option.value && (
                          <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                        )}
                      </div>
                      <div className="font-medium">{option.label}</div>
                    </div>
                  </div>
                  {option.hasInput && currentAnswer === option.value && (
                    <Textarea
                      placeholder="Descreva detalhadamente..."
                      className="mt-2"
                      value={answers[`${questionId}_input`] || ''}
                      onChange={(e) => handleAnswer(`${questionId}_input`, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">{currentQuestion.question}</h2>
            <p className="text-gray-600">Tipo de pergunta não implementado: {currentQuestion.type}</p>
          </div>
        );
    }
  };

  const isCurrentStepValid = () => {
    const questionId = currentQuestion.id;
    const answer = answers[questionId];
    
    if (!currentQuestion.required) return true;
    
    switch (currentQuestion.type) {
      case 'single_choice':
      case 'text_with_option':
      case 'pharma_usage':
        return answer !== undefined && answer !== '';
      
      case 'multiple_choice':
        return Array.isArray(answer) && answer.length > 0;
      
      case 'personal_data':
        return currentQuestion.fields.every(field => {
          const fieldAnswer = answers[`personal_${field.name}`];
          return !field.required || (fieldAnswer !== undefined && fieldAnswer !== '');
        });
      
      default:
        return true;
    }
  };

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-2xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">E</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Vamos conhecer você melhor
          </h1>
          <p className="text-gray-600">
            Responda algumas perguntas para personalizarmos sua experiência
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">
              Pergunta {currentStep + 1} de {totalSteps}
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(progress)}%
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Question Card */}
        <Card className="mb-8">
          <CardContent className="p-6">
            {error && (
              <Alert className="mb-6 border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}
            
            {renderQuestion()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Anterior</span>
          </Button>

          <Button
            onClick={handleNext}
            disabled={!isCurrentStepValid() || isLoading}
            className="flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : currentStep === totalSteps - 1 ? (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Finalizar</span>
              </>
            ) : (
              <>
                <span>Próxima</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingOriginal;

