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
import { ArrowLeft, ArrowRight, CheckCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../hooks/useFirebaseAuth.jsx';
import { anamneseQuestions, calculateBMR, calculateTDEE, calculateBMI, classifyBMI, calculateMacros } from '../data/anamneseQuestions';

const OnboardingPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user, updateUserProfile } = useAuth();
  const navigate = useNavigate();

  const totalSteps = anamneseQuestions.length;
  const progress = ((currentStep + 1) / totalSteps) * 100;
  const currentQuestion = anamneseQuestions[currentStep];

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleComplete = async () => {
    try {
      setIsLoading(true);
      setError('');

      // Calcular métricas baseadas nas respostas
      const personalInfo = answers.personal_info || {};
      const activityLevel = answers.activity_level;
      const primaryGoal = answers.primary_goal;

      let calculations = {};
      
      if (personalInfo.weight && personalInfo.height && personalInfo.age && personalInfo.gender) {
        const bmr = calculateBMR(
          parseFloat(personalInfo.weight),
          parseFloat(personalInfo.height),
          parseInt(personalInfo.age),
          personalInfo.gender
        );
        
        const tdee = calculateTDEE(bmr, activityLevel);
        const bmi = calculateBMI(parseFloat(personalInfo.weight), parseFloat(personalInfo.height));
        const bmiClassification = classifyBMI(bmi);
        
        // Ajustar calorias baseado no objetivo
        let targetCalories = tdee;
        if (primaryGoal === 'weight_loss') {
          targetCalories = tdee * 0.8; // Déficit de 20%
        } else if (primaryGoal === 'muscle_gain') {
          targetCalories = tdee * 1.1; // Superávit de 10%
        }
        
        const macros = calculateMacros(targetCalories, primaryGoal);

        calculations = {
          bmr: Math.round(bmr),
          tdee: Math.round(tdee),
          bmi: Math.round(bmi * 10) / 10,
          bmiClassification,
          targetCalories: Math.round(targetCalories),
          macros
        };
      }

      // Salvar dados no perfil do usuário
      const profileData = {
        profile: {
          onboardingCompleted: true,
          anamneseCompleted: true,
          anamneseAnswers: answers,
          calculations,
          completedAt: new Date().toISOString()
        }
      };

      await updateUserProfile(profileData);
      
      // Redirecionar para o dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Erro ao completar onboarding:', error);
      setError('Erro ao salvar suas informações. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const isCurrentStepValid = () => {
    const questionId = currentQuestion.id;
    const answer = answers[questionId];

    if (currentQuestion.type === 'form') {
      // Verificar se todos os campos obrigatórios estão preenchidos
      return currentQuestion.fields.every(field => {
        if (field.required) {
          return answer && answer[field.id] !== undefined && answer[field.id] !== '';
        }
        return true;
      });
    } else if (currentQuestion.type === 'single_choice') {
      return answer !== undefined;
    } else if (currentQuestion.type === 'multiple_choice') {
      return answer && Array.isArray(answer) && answer.length > 0;
    } else if (currentQuestion.type === 'text_area') {
      // Campo de texto não é obrigatório por padrão
      return true;
    }

    return false;
  };

  const renderQuestion = () => {
    const questionId = currentQuestion.id;
    const answer = answers[questionId] || {};

    switch (currentQuestion.type) {
      case 'form':
        return (
          <div className="space-y-4">
            {currentQuestion.fields.map(field => (
              <div key={field.id} className="space-y-2">
                <Label htmlFor={field.id}>
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
                
                {field.type === 'select' ? (
                  <Select
                    value={answer[field.id] || ''}
                    onValueChange={(value) => handleAnswer(questionId, { ...answer, [field.id]: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={field.placeholder || 'Selecione...'} />
                    </SelectTrigger>
                    <SelectContent>
                      {field.options.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    id={field.id}
                    type={field.type}
                    placeholder={field.placeholder}
                    min={field.min}
                    max={field.max}
                    step={field.step}
                    value={answer[field.id] || ''}
                    onChange={(e) => handleAnswer(questionId, { ...answer, [field.id]: e.target.value })}
                  />
                )}
              </div>
            ))}
          </div>
        );

      case 'single_choice':
        return (
          <div className="space-y-3">
            {currentQuestion.options.map(option => (
              <Card 
                key={option.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  answers[questionId] === option.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => handleAnswer(questionId, option.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      answers[questionId] === option.id 
                        ? 'bg-blue-500 border-blue-500' 
                        : 'border-gray-300'
                    }`}>
                      {answers[questionId] === option.id && (
                        <div className="w-2 h-2 bg-white rounded-full m-0.5" />
                      )}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium">{option.label}</h4>
                      {option.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {option.description}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      case 'multiple_choice':
        const selectedOptions = answers[questionId] || [];
        return (
          <div className="space-y-3">
            {currentQuestion.options.map(option => (
              <Card 
                key={option.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedOptions.includes(option.id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => {
                  const newSelection = selectedOptions.includes(option.id)
                    ? selectedOptions.filter(id => id !== option.id)
                    : [...selectedOptions, option.id];
                  handleAnswer(questionId, newSelection);
                }}
              >
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Checkbox 
                      checked={selectedOptions.includes(option.id)}
                      readOnly
                    />
                    <div className="flex-1">
                      <h4 className="font-medium">{option.label}</h4>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      case 'text_area':
        return (
          <div className="space-y-2">
            <Textarea
              placeholder={currentQuestion.placeholder}
              value={answers[questionId] || ''}
              onChange={(e) => handleAnswer(questionId, e.target.value)}
              rows={4}
            />
          </div>
        );

      default:
        return <div>Tipo de pergunta não suportado</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">E</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Vamos conhecer você melhor
          </h1>
          <p className="text-gray-600">
            Responda algumas perguntas para personalizarmos sua experiência
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-muted-foreground">
              Pergunta {currentStep + 1} de {totalSteps}
            </span>
            <span className="text-sm font-medium">
              {Math.round(progress)}%
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Question Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">
              {currentQuestion.title}
            </CardTitle>
            {currentQuestion.subtitle && (
              <CardDescription className="text-base">
                {currentQuestion.subtitle}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
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
            disabled={currentStep === 0 || isLoading}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Anterior
          </Button>

          <Button
            onClick={handleNext}
            disabled={!isCurrentStepValid() || isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : currentStep === totalSteps - 1 ? (
              <>
                Finalizar
                <CheckCircle className="ml-2 h-4 w-4" />
              </>
            ) : (
              <>
                Próxima
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;

