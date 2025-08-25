import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Activity, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Code, 
  Smartphone, 
  Target,
  Calendar,
  GitBranch,
  Users,
  Zap,
  Loader2,
  Wifi,
  WifiOff
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { motion } from 'framer-motion'
import './App.css'

// Import custom hooks
import { 
  useProgress, 
  useFeaturesProgress, 
  useProgressTimeline, 
  useServicesStatus, 
  useRecentActivity 
} from './hooks/useApi'
import { 
  useWebSocket, 
  useProgressUpdates, 
  useRealTimeNotifications 
} from './hooks/useWebSocket'

function LoadingSpinner({ size = 'default' }) {
  const sizeClasses = {
    small: 'h-4 w-4',
    default: 'h-6 w-6',
    large: 'h-8 w-8'
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]}`} />
  );
}

function ErrorAlert({ error, onRetry }) {
  return (
    <Alert variant="destructive">
      <AlertTriangle className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>Erro: {error}</span>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry}>
            Tentar novamente
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}

function ConnectionStatus({ connected }) {
  return (
    <div className="flex items-center gap-2">
      {connected ? (
        <>
          <Wifi className="h-4 w-4 text-green-500" />
          <span className="text-sm text-green-600">Conectado</span>
        </>
      ) : (
        <>
          <WifiOff className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-600">Desconectado</span>
        </>
      )}
    </div>
  );
}

function ProgressCard({ title, progress, status, tasks, completed, icon: Icon, color, loading, error }) {
  const statusColors = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500',
    critical: 'bg-red-500',
    in_progress: 'bg-blue-500'
  }

  if (loading) {
    return (
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Icon className={`h-4 w-4 ${color}`} />
            {title}
          </CardTitle>
          <LoadingSpinner size="small" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-8 bg-muted animate-pulse rounded" />
            <div className="h-2 bg-muted animate-pulse rounded" />
            <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="relative overflow-hidden border-red-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Icon className={`h-4 w-4 ${color}`} />
            {title}
          </CardTitle>
          <AlertTriangle className="h-4 w-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">Erro ao carregar dados</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Icon className={`h-4 w-4 ${color}`} />
            {title}
          </CardTitle>
          <div className={`w-2 h-2 rounded-full ${statusColors[status] || statusColors.in_progress}`} />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold mb-2">{progress}%</div>
          <Progress value={progress} className="mb-2" />
          <p className="text-xs text-muted-foreground">
            {completed} de {tasks} tarefas concluídas
          </p>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function FeatureCard({ feature, loading }) {
  const priorityColors = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-blue-100 text-blue-800 border-blue-200'
  }

  const statusIcons = {
    completed: <CheckCircle className="h-4 w-4 text-green-500" />,
    in_progress: <Activity className="h-4 w-4 text-blue-500" />,
    pending: <Clock className="h-4 w-4 text-gray-500" />,
    blocked: <AlertTriangle className="h-4 w-4 text-red-500" />
  }

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="space-y-2">
            <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
            <div className="h-6 bg-muted animate-pulse rounded w-1/2" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-4 bg-muted animate-pulse rounded" />
            <div className="h-2 bg-muted animate-pulse rounded" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">{feature.name}</CardTitle>
            {statusIcons[feature.status]}
          </div>
          <Badge className={`w-fit text-xs ${priorityColors[feature.priority]}`}>
            {feature.priority}
          </Badge>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progresso</span>
              <span className="font-medium">{feature.progress}%</span>
            </div>
            <Progress value={feature.progress} />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function ServiceStatus({ service }) {
  const statusColors = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500',
    critical: 'bg-red-500'
  }

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${statusColors[service.status]}`} />
        <span className="font-medium">{service.name}</span>
      </div>
      <div className="flex gap-4 text-sm text-muted-foreground">
        <span>Uptime: {service.uptime}</span>
        <span>Response: {service.response}</span>
      </div>
    </div>
  )
}

function ActivityItem({ activity }) {
  const typeIcons = {
    commit: <GitBranch className="h-4 w-4 text-blue-500" />,
    deploy: <Zap className="h-4 w-4 text-green-500" />,
    milestone: <Target className="h-4 w-4 text-purple-500" />,
    alert: <AlertTriangle className="h-4 w-4 text-red-500" />,
    update: <Activity className="h-4 w-4 text-blue-500" />
  }

  return (
    <div className="flex items-start gap-3 p-3 border rounded-lg">
      {typeIcons[activity.type] || typeIcons.update}
      <div className="flex-1">
        <p className="text-sm font-medium">{activity.message}</p>
        <p className="text-xs text-muted-foreground">
          {activity.author} • {activity.time}
        </p>
      </div>
    </div>
  )
}

function App() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [realtimeUpdates, setRealtimeUpdates] = useState([])

  // API hooks
  const { data: progressData, loading: progressLoading, error: progressError, refetch: refetchProgress } = useProgress()
  const { data: featuresData, loading: featuresLoading, error: featuresError, refetch: refetchFeatures } = useFeaturesProgress()
  const { data: timelineData, loading: timelineLoading, error: timelineError, refetch: refetchTimeline } = useProgressTimeline()
  const { data: servicesData, loading: servicesLoading, error: servicesError, refetch: refetchServices } = useServicesStatus()
  const { data: activityData, loading: activityLoading, error: activityError, refetch: refetchActivity } = useRecentActivity()

  // WebSocket hooks
  const { connected, subscribeToProgress } = useWebSocket()
  
  const progressUpdates = useProgressUpdates(useCallback((update) => {
    console.log('📊 Novo update de progresso:', update)
    setRealtimeUpdates(prev => [`Progresso atualizado: ${update.message}`, ...prev.slice(0, 4)])
    // Refresh relevant data when update received
    refetchProgress()
    refetchFeatures()
  }, [refetchProgress, refetchFeatures]))

  const notifications = useRealTimeNotifications(useCallback((notification) => {
    console.log('🔔 Nova notificação:', notification)
    setRealtimeUpdates(prev => [`Notificação: ${notification.message}`, ...prev.slice(0, 4)])
  }, []))

  // Subscribe to progress updates for EvolveYou repositories
  useEffect(() => {
    if (connected) {
      subscribeToProgress(['evolveyou-backend', 'evolveyou-frontend', 'evolveyou-dashboard-frontend', 'evolveyou-dashboard-backend'])
    }
  }, [connected, subscribeToProgress])

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Calculate overall progress from real data
  const overallProgress = progressData?.overall || 0
  const daysRemaining = progressData?.daysRemaining || 0
  const activeTasks = progressData?.activeTasks || 0

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center"
              >
                <Zap className="h-4 w-4 text-white" />
              </motion.div>
              <div>
                <h1 className="text-xl font-bold">EvolveYou Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Progresso geral: {overallProgress}% • {daysRemaining} dias restantes
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ConnectionStatus connected={connected} />
              {realtimeUpdates.length > 0 && (
                <Badge variant="outline" className="gap-1 animate-pulse">
                  <Zap className="h-3 w-3 text-green-500" />
                  {realtimeUpdates.length} updates
                </Badge>
              )}
              <Badge variant="outline" className="gap-1">
                <Activity className="h-3 w-3" />
                {activeTasks} tarefas ativas
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Users className="h-3 w-3" />
                1 agente
              </Badge>
              <div className="text-sm text-muted-foreground">
                {currentTime.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Global error handling */}
        {progressError && (
          <div className="mb-6">
            <ErrorAlert error={progressError} onRetry={refetchProgress} />
          </div>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="features">Funcionalidades</TabsTrigger>
            <TabsTrigger value="services">Serviços</TabsTrigger>
            <TabsTrigger value="activity">Atividade</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Cards de Progresso Principal */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ProgressCard
                title="Backend"
                progress={progressData?.components?.backend?.progress || 0}
                status={progressData?.components?.backend?.status || 'in_progress'}
                tasks={progressData?.components?.backend?.tasks || 0}
                completed={progressData?.components?.backend?.completed || 0}
                icon={Code}
                color="text-blue-500"
                loading={progressLoading}
                error={progressError}
              />
              <ProgressCard
                title="Frontend"
                progress={progressData?.components?.frontend?.progress || 0}
                status={progressData?.components?.frontend?.status || 'in_progress'}
                tasks={progressData?.components?.frontend?.tasks || 0}
                completed={progressData?.components?.frontend?.completed || 0}
                icon={Smartphone}
                color="text-green-500"
                loading={progressLoading}
                error={progressError}
              />
              <ProgressCard
                title="Funcionalidades"
                progress={progressData?.components?.features?.progress || 0}
                status={progressData?.components?.features?.status || 'warning'}
                tasks={progressData?.components?.features?.tasks || 0}
                completed={progressData?.components?.features?.completed || 0}
                icon={Target}
                color="text-purple-500"
                loading={progressLoading}
                error={progressError}
              />
            </div>

            {/* Gráfico de Timeline */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Timeline de Progresso
                  {timelineLoading && <LoadingSpinner size="small" />}
                </CardTitle>
                <CardDescription>
                  Comparação entre progresso planejado vs. real
                </CardDescription>
              </CardHeader>
              <CardContent>
                {timelineLoading ? (
                  <div className="h-[300px] flex items-center justify-center">
                    <LoadingSpinner />
                  </div>
                ) : timelineError ? (
                  <div className="h-[300px] flex items-center justify-center">
                    <p className="text-red-600">Erro ao carregar timeline</p>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={timelineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="week" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="planned" 
                        stroke="#8884d8" 
                        strokeDasharray="5 5"
                        name="Planejado"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="actual" 
                        stroke="#82ca9d" 
                        strokeWidth={3}
                        name="Real"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* Métricas Rápidas */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Dias Restantes</p>
                      <p className="text-xl font-bold">
                        {progressLoading ? <LoadingSpinner size="small" /> : daysRemaining}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Concluídas</p>
                      <p className="text-xl font-bold">
                        {progressLoading ? <LoadingSpinner size="small" /> : progressData?.completedTasks || 0}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Em Progresso</p>
                      <p className="text-xl font-bold">
                        {progressLoading ? <LoadingSpinner size="small" /> : activeTasks}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Bloqueadas</p>
                      <p className="text-xl font-bold">
                        {progressLoading ? <LoadingSpinner size="small" /> : progressData?.blockedTasks || 0}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="features" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Funcionalidades</h2>
                <p className="text-muted-foreground">
                  Status detalhado de todas as funcionalidades do projeto
                </p>
              </div>
              <Button>
                <Target className="h-4 w-4 mr-2" />
                Adicionar Marco
              </Button>
            </div>

            {featuresError && (
              <ErrorAlert error={featuresError} />
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {featuresLoading ? (
                // Loading skeleton
                Array.from({ length: 6 }).map((_, index) => (
                  <FeatureCard key={index} feature={{}} loading={true} />
                ))
              ) : featuresData ? (
                featuresData.map((feature, index) => (
                  <FeatureCard key={index} feature={feature} />
                ))
              ) : (
                <div className="col-span-full text-center py-8">
                  <p className="text-muted-foreground">Nenhuma funcionalidade encontrada</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="services" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Status dos Serviços</h2>
              <p className="text-muted-foreground">
                Monitoramento em tempo real de todos os microserviços
              </p>
            </div>

            {servicesError && (
              <ErrorAlert error={servicesError} />
            )}

            {servicesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="h-16 bg-muted animate-pulse rounded-lg" />
                ))}
              </div>
            ) : servicesData ? (
              <div className="space-y-3">
                {servicesData.map((service, index) => (
                  <ServiceStatus key={index} service={service} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Nenhum serviço encontrado</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="activity" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Atividade Recente</h2>
              <p className="text-muted-foreground">
                Histórico de commits, deploys e marcos atingidos
              </p>
            </div>

            {activityError && (
              <ErrorAlert error={activityError} />
            )}

            {activityLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, index) => (
                  <div key={index} className="h-20 bg-muted animate-pulse rounded-lg" />
                ))}
              </div>
            ) : activityData ? (
              <div className="space-y-3">
                {activityData.map((activity, index) => (
                  <ActivityItem key={index} activity={activity} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Nenhuma atividade encontrada</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

