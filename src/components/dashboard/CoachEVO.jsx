import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Send, Bot, User, Sparkles, MessageCircle } from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';

const CoachEVO = ({ userProfile }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Olá! Eu sou o Coach EVO, seu assistente pessoal de fitness e nutrição. 🚀\n\nBaseado no seu perfil, vejo que seu objetivo é ${
        userProfile.anamneseAnswers?.primary_goal === 'weight_loss' ? 'perder peso' :
        userProfile.anamneseAnswers?.primary_goal === 'muscle_gain' ? 'ganhar massa muscular' :
        userProfile.anamneseAnswers?.primary_goal === 'maintenance' ? 'manter o peso' :
        userProfile.anamneseAnswers?.primary_goal === 'performance' ? 'melhorar performance' : 'melhorar sua saúde'
      }. Estou aqui para te ajudar com dicas personalizadas, esclarecer dúvidas e te motivar nessa jornada!\n\nComo posso te ajudar hoje?`,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Respostas baseadas no perfil do usuário
    const personalInfo = userProfile.anamneseAnswers?.personal_info || {};
    const calculations = userProfile.calculations || {};
    const primaryGoal = userProfile.anamneseAnswers?.primary_goal;
    
    // Respostas contextuais baseadas em palavras-chave
    if (lowerMessage.includes('dieta') || lowerMessage.includes('alimentação') || lowerMessage.includes('comida')) {
      if (primaryGoal === 'weight_loss') {
        return `Para seu objetivo de perda de peso, recomendo:\n\n🥗 Mantenha um déficit calórico de ~${Math.round((calculations.tdee || 2000) * 0.2)} kcal\n🍗 Consuma ${calculations.macros?.protein.grams || 120}g de proteína por dia\n🥬 Priorize vegetais e fibras\n💧 Beba pelo menos 2.5L de água\n\nQuer que eu crie um plano alimentar específico para você?`;
      } else if (primaryGoal === 'muscle_gain') {
        return `Para ganho de massa muscular:\n\n💪 Mantenha superávit calórico de ${Math.round((calculations.tdee || 2000) * 0.1)} kcal\n🥩 ${calculations.macros?.protein.grams || 140}g de proteína diariamente\n🍚 ${calculations.macros?.carbs.grams || 200}g de carboidratos para energia\n⏰ Refeições a cada 3-4 horas\n\nPrecisa de sugestões de refeições?`;
      }
      return `Baseado no seu perfil, sua meta calórica é ${calculations.targetCalories || 2000} kcal/dia. Quer dicas específicas sobre algum aspecto da alimentação?`;
    }
    
    if (lowerMessage.includes('treino') || lowerMessage.includes('exercício') || lowerMessage.includes('academia')) {
      const activityLevel = userProfile.anamneseAnswers?.activity_level;
      if (activityLevel === 'sedentary' || activityLevel === 'light') {
        return `Vejo que você está começando! Recomendo:\n\n🚶‍♀️ Comece com 3x/semana\n💪 Treino funcional ou musculação básica\n⏱️ 45-60 minutos por sessão\n📈 Aumente gradualmente a intensidade\n\nQuer um plano de treino personalizado?`;
      } else {
        return `Para seu nível de atividade, sugiro:\n\n🏋️‍♀️ 4-5x por semana\n🎯 Treino dividido por grupos musculares\n⚡ Inclua cardio 2-3x/semana\n💤 Descanso adequado entre treinos\n\nPrecisa de ajuda com algum exercício específico?`;
      }
    }
    
    if (lowerMessage.includes('peso') || lowerMessage.includes('balança')) {
      const currentWeight = parseFloat(personalInfo.weight) || 0;
      const targetWeight = parseFloat(userProfile.anamneseAnswers?.target_weight?.target_weight) || currentWeight;
      const difference = Math.abs(currentWeight - targetWeight);
      
      return `Seu peso atual é ${currentWeight}kg e sua meta é ${targetWeight}kg.\n\n${
        currentWeight > targetWeight 
          ? `📉 Você precisa perder ${difference.toFixed(1)}kg\n🎯 Perda saudável: 0.5-1kg por semana\n⏰ Tempo estimado: ${Math.ceil(difference / 0.75)} semanas`
          : currentWeight < targetWeight
          ? `📈 Você precisa ganhar ${difference.toFixed(1)}kg\n🎯 Ganho saudável: 0.3-0.5kg por semana\n⏰ Tempo estimado: ${Math.ceil(difference / 0.4)} semanas`
          : '🎉 Você já está no seu peso ideal! Foque em manter e melhorar a composição corporal.'
      }\n\nQuer dicas para acelerar o processo?`;
    }
    
    if (lowerMessage.includes('água') || lowerMessage.includes('hidratação')) {
      const recommendedWater = Math.round((parseFloat(personalInfo.weight) || 70) * 35);
      return `💧 Baseado no seu peso (${personalInfo.weight || 70}kg), você deve beber aproximadamente ${(recommendedWater/1000).toFixed(1)}L de água por dia.\n\n✅ Dicas para se manter hidratado:\n• Beba 1 copo ao acordar\n• 1 copo antes de cada refeição\n• Tenha sempre uma garrafa por perto\n• Use apps para lembrar\n\nEstá conseguindo bater essa meta?`;
    }
    
    if (lowerMessage.includes('motivação') || lowerMessage.includes('desanimado') || lowerMessage.includes('difícil')) {
      return `Eu entendo que às vezes é difícil! 💪 Lembre-se:\n\n🌟 Você já deu o primeiro passo ao começar\n📈 Progresso não é linear - altos e baixos são normais\n🎯 Foque em pequenas vitórias diárias\n👥 Você não está sozinho nessa jornada\n\n"O sucesso é a soma de pequenos esforços repetidos dia após dia."\n\nConte comigo para te apoiar! O que está te desafiando mais?`;
    }
    
    if (lowerMessage.includes('imc') || lowerMessage.includes('índice')) {
      const bmi = calculations.bmi;
      const classification = calculations.bmiClassification;
      return `Seu IMC atual é ${bmi || 'não calculado'}${classification ? ` - ${classification.category}` : ''}.\n\n${
        bmi < 18.5 ? '📈 Foque em ganhar peso de forma saudável com exercícios e boa alimentação' :
        bmi < 25 ? '🎉 Parabéns! Seu IMC está na faixa ideal. Continue assim!' :
        bmi < 30 ? '⚠️ Você está com sobrepeso. Vamos trabalhar juntos para melhorar!' :
        '🚨 É importante cuidar da saúde. Recomendo acompanhamento médico junto com nosso plano.'
      }\n\nLembre-se: IMC é apenas um indicador. Composição corporal também é importante!`;
    }
    
    // Respostas genéricas amigáveis
    const genericResponses = [
      `Ótima pergunta! Com base no seu perfil, posso te dar dicas mais específicas. ${
        primaryGoal === 'weight_loss' ? 'Para perda de peso, foque em déficit calórico e exercícios regulares.' :
        primaryGoal === 'muscle_gain' ? 'Para ganho de massa, priorize proteína e treino de força.' :
        'Consistência é a chave para qualquer objetivo!'
      } O que mais posso esclarecer?`,
      
      `Entendi sua dúvida! Baseado nos seus dados (${personalInfo.age || 'N/A'} anos, ${personalInfo.weight || 'N/A'}kg), ${
        calculations.targetCalories ? `sua meta calórica é ${calculations.targetCalories} kcal/dia.` : 'posso te ajudar com orientações personalizadas.'
      } Tem alguma situação específica?`,
      
      `Vamos resolver isso juntos! 🤝 Seu perfil mostra que você está no caminho certo. ${
        userProfile.anamneseAnswers?.activity_level === 'sedentary' ? 'Que tal começarmos com pequenas mudanças na rotina?' :
        'Continue com essa dedicação!'
      } Como posso te apoiar melhor?`
    ];
    
    return genericResponses[Math.floor(Math.random() * genericResponses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simular delay da resposta do bot
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        type: 'bot',
        content: generateBotResponse(inputMessage),
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000 + Math.random() * 2000); // 1-3 segundos
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "Como devo ajustar minha dieta?",
    "Que exercícios são melhores para mim?",
    "Como acelerar meus resultados?",
    "Estou sem motivação, me ajude!"
  ];

  return (
    <div className="space-y-6">
      {/* Header do Coach */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2">
                Coach EVO
                <Badge variant="secondary" className="gap-1">
                  <Sparkles className="h-3 w-3" />
                  IA
                </Badge>
              </CardTitle>
              <CardDescription>
                Seu assistente pessoal de fitness e nutrição, disponível 24/7
              </CardDescription>
            </div>
            <Badge variant="outline" className="gap-1 text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Online
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Chat Interface */}
      <Card className="h-[600px] flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Conversa com o Coach
          </CardTitle>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages Area */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.type === 'bot' && (
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-muted'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm">
                      {message.content}
                    </div>
                    <div className={`text-xs mt-1 opacity-70 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-muted-foreground'
                    }`}>
                      {message.timestamp}
                    </div>
                  </div>
                  
                  {message.type === 'user' && (
                    <Avatar className="w-8 h-8">
                      <AvatarFallback>
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg p-3">
                    <LoadingSpinner size="small" />
                    <span className="text-sm text-muted-foreground ml-2">
                      Coach EVO está digitando...
                    </span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Quick Questions */}
          <div className="p-4 border-t">
            <div className="mb-3">
              <p className="text-sm text-muted-foreground mb-2">Perguntas rápidas:</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => setInputMessage(question)}
                    disabled={isLoading}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="flex gap-2">
              <Input
                placeholder="Digite sua pergunta ou dúvida..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CoachEVO;

