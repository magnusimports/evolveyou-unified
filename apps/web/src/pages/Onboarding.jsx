import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

const Onboarding = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    birth_date: '',
    gender: '',
    height: '',
    weight: '',
    activity_level: '',
    goal: '',
    target_weight: '',
    training_days: [],
    training_duration: '',
    preferred_exercises: [],
    dietary_restrictions: [],
    dietary_preferences: [],
    meals_per_day: 3,
  });

  const { completeOnboarding } = useAuth();
  const navigate = useNavigate();

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    if (error) setError('');
  };

  const handleArrayToggle = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');

    try {
      await completeOnboarding(formData);
      navigate('/dashboard');
    } catch (error) {
      setError(error.message || 'Erro ao completar onboarding');
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Informações Pessoais</h2>
              <p className="text-gray-600">Vamos conhecer você melhor</p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="birth_date">Data de Nascimento</Label>
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => handleInputChange('birth_date', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Gênero</Label>
                <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione seu gênero" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="masculino">Masculino</SelectItem>
                    <SelectItem value="feminino">Feminino</SelectItem>
                    <SelectItem value="outro">Outro</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="height">Altura (cm)</Label>
                  <Input
                    id="height"
                    type="number"
                    placeholder="170"
                    value={formData.height}
                    onChange={(e) => handleInputChange('height', parseFloat(e.target.value))}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="weight">Peso (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    placeholder="70"
                    value={formData.weight}
                    onChange={(e) => handleInputChange('weight', parseFloat(e.target.value))}
                    required
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Nível de Atividade</h2>
              <p className="text-gray-600">Como você descreveria seu estilo de vida?</p>
            </div>

            <div className="space-y-3">
              {[
                { value: 'sedentario', label: 'Sedentário', desc: 'Pouco ou nenhum exercício' },
                { value: 'levemente_ativo', label: 'Levemente Ativo', desc: 'Exercício leve 1-3 dias/semana' },
                { value: 'moderadamente_ativo', label: 'Moderadamente Ativo', desc: 'Exercício moderado 3-5 dias/semana' },
                { value: 'muito_ativo', label: 'Muito Ativo', desc: 'Exercício pesado 6-7 dias/semana' },
                { value: 'extremamente_ativo', label: 'Extremamente Ativo', desc: 'Exercício muito pesado, trabalho físico' },
              ].map((option) => (
                <Card 
                  key={option.value}
                  className={`cursor-pointer transition-colors ${
                    formData.activity_level === option.value ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('activity_level', option.value)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        formData.activity_level === option.value ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
                      }`} />
                      <div>
                        <h3 className="font-medium">{option.label}</h3>
                        <p className="text-sm text-gray-600">{option.desc}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Seus Objetivos</h2>
              <p className="text-gray-600">Qual é seu principal objetivo?</p>
            </div>

            <div className="space-y-3">
              {[
                { value: 'perder_peso', label: 'Perder Peso', desc: 'Reduzir gordura corporal' },
                { value: 'ganhar_peso', label: 'Ganhar Peso', desc: 'Aumentar massa muscular' },
                { value: 'manter_peso', label: 'Manter Peso', desc: 'Manter forma física atual' },
              ].map((option) => (
                <Card 
                  key={option.value}
                  className={`cursor-pointer transition-colors ${
                    formData.goal === option.value ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleInputChange('goal', option.value)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        formData.goal === option.value ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
                      }`} />
                      <div>
                        <h3 className="font-medium">{option.label}</h3>
                        <p className="text-sm text-gray-600">{option.desc}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {(formData.goal === 'perder_peso' || formData.goal === 'ganhar_peso') && (
              <div className="space-y-2">
                <Label htmlFor="target_weight">Peso Meta (kg)</Label>
                <Input
                  id="target_weight"
                  type="number"
                  placeholder="65"
                  value={formData.target_weight}
                  onChange={(e) => handleInputChange('target_weight', parseFloat(e.target.value))}
                />
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Preferências de Treino</h2>
              <p className="text-gray-600">Vamos personalizar seus treinos</p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Dias da semana para treinar</Label>
                <div className="grid grid-cols-2 gap-2">
                  {['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'].map((day) => (
                    <div key={day} className="flex items-center space-x-2">
                      <Checkbox
                        id={day}
                        checked={formData.training_days.includes(day)}
                        onCheckedChange={() => handleArrayToggle('training_days', day)}
                      />
                      <Label htmlFor={day} className="capitalize">{day}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Duração média do treino</Label>
                <Select value={formData.training_duration.toString()} onValueChange={(value) => handleInputChange('training_duration', parseInt(value))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a duração" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">30 minutos</SelectItem>
                    <SelectItem value="45">45 minutos</SelectItem>
                    <SelectItem value="60">1 hora</SelectItem>
                    <SelectItem value="90">1h30min</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Tipos de exercício preferidos</Label>
                <div className="grid grid-cols-2 gap-2">
                  {['musculacao', 'cardio', 'funcional', 'yoga', 'pilates', 'natacao'].map((exercise) => (
                    <div key={exercise} className="flex items-center space-x-2">
                      <Checkbox
                        id={exercise}
                        checked={formData.preferred_exercises.includes(exercise)}
                        onCheckedChange={() => handleArrayToggle('preferred_exercises', exercise)}
                      />
                      <Label htmlFor={exercise} className="capitalize">{exercise}</Label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.birth_date && formData.gender && formData.height && formData.weight;
      case 2:
        return formData.activity_level;
      case 3:
        return formData.goal;
      case 4:
        return formData.training_days.length > 0 && formData.training_duration;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle>Configuração Inicial</CardTitle>
                <CardDescription>
                  Etapa {currentStep} de {totalSteps}
                </CardDescription>
              </div>
              <div className="text-sm text-gray-600">
                {Math.round(progress)}%
              </div>
            </div>
            <Progress value={progress} className="w-full" />
          </CardHeader>

          <CardContent className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {renderStep()}

            <div className="flex justify-between pt-6">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Anterior
              </Button>

              {currentStep === totalSteps ? (
                <Button
                  onClick={handleSubmit}
                  disabled={!isStepValid() || loading}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Finalizando...
                    </>
                  ) : (
                    'Finalizar'
                  )}
                </Button>
              ) : (
                <Button
                  onClick={nextStep}
                  disabled={!isStepValid()}
                >
                  Próximo
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Onboarding;

