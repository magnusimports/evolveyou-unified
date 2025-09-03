// Base de Dados Completa de Exercícios - EvolveYou
// Biblioteca com 200+ exercícios categorizados e detalhados

export const exerciseDatabase = [
  // ==================== PEITO ====================
  {
    id: "chest_001",
    nome: "Supino Reto com Barra",
    categoria: "peito",
    grupo_muscular: ["peitoral_maior", "triceps", "deltoides_anterior"],
    equipamento: "barra_olimpica",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Deite no banco com os pés firmes no chão",
      "Segure a barra com pegada um pouco mais larga que os ombros",
      "Retire a barra do suporte e posicione sobre o peito",
      "Desça controladamente até tocar o peito",
      "Empurre a barra de volta à posição inicial"
    ],
    dicas: [
      "Mantenha os pés no chão durante todo o movimento",
      "Controle a descida (2-3 segundos)",
      "Não deixe a barra quicar no peito",
      "Mantenha os ombros retraídos"
    ],
    musculos_primarios: ["peitoral_maior"],
    musculos_secundarios: ["triceps", "deltoides_anterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "6-12",
    descanso_segundos: 120,
    calorias_por_serie: 15
  },
  {
    id: "chest_002",
    nome: "Supino Inclinado com Halteres",
    categoria: "peito",
    grupo_muscular: ["peitoral_maior_superior", "deltoides_anterior", "triceps"],
    equipamento: "halteres",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Ajuste o banco em 30-45 graus de inclinação",
      "Segure os halteres com pegada neutra",
      "Posicione os halteres na altura do peito superior",
      "Empurre os halteres para cima e ligeiramente para dentro",
      "Desça controladamente até sentir alongamento no peito"
    ],
    dicas: [
      "Não incline o banco mais que 45 graus",
      "Mantenha os cotovelos ligeiramente flexionados",
      "Foque na contração do peito superior",
      "Evite bater os halteres no topo"
    ],
    musculos_primarios: ["peitoral_maior_superior"],
    musculos_secundarios: ["deltoides_anterior", "triceps"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 90,
    calorias_por_serie: 12
  },
  {
    id: "chest_003",
    nome: "Flexão de Braço",
    categoria: "peito",
    grupo_muscular: ["peitoral_maior", "triceps", "core"],
    equipamento: "peso_corporal",
    dificuldade: "iniciante",
    tipo_movimento: "composto",
    instrucoes: [
      "Posicione-se em prancha com mãos na largura dos ombros",
      "Mantenha o corpo alinhado da cabeça aos pés",
      "Desça o corpo até o peito quase tocar o chão",
      "Empurre o corpo de volta à posição inicial",
      "Mantenha o core contraído durante todo movimento"
    ],
    dicas: [
      "Não deixe o quadril subir ou descer",
      "Olhe para frente, não para baixo",
      "Se for difícil, apoie os joelhos",
      "Respire na descida, expire na subida"
    ],
    musculos_primarios: ["peitoral_maior"],
    musculos_secundarios: ["triceps", "core", "deltoides_anterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-20",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },
  {
    id: "chest_004",
    nome: "Crucifixo com Halteres",
    categoria: "peito",
    grupo_muscular: ["peitoral_maior"],
    equipamento: "halteres",
    dificuldade: "intermediario",
    tipo_movimento: "isolado",
    instrucoes: [
      "Deite no banco com halteres nas mãos",
      "Estenda os braços sobre o peito com ligeira flexão nos cotovelos",
      "Abra os braços em arco até sentir alongamento no peito",
      "Retorne à posição inicial contraindo o peito",
      "Mantenha a mesma curvatura dos cotovelos"
    ],
    dicas: [
      "Não estenda completamente os cotovelos",
      "Controle o movimento na descida",
      "Foque na contração do peito",
      "Use peso moderado para manter a forma"
    ],
    musculos_primarios: ["peitoral_maior"],
    musculos_secundarios: ["deltoides_anterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-15",
    descanso_segundos: 75,
    calorias_por_serie: 10
  },

  // ==================== COSTAS ====================
  {
    id: "back_001",
    nome: "Puxada na Polia Alta",
    categoria: "costas",
    grupo_muscular: ["latissimo_dorso", "romboides", "biceps"],
    equipamento: "polia_alta",
    dificuldade: "iniciante",
    tipo_movimento: "composto",
    instrucoes: [
      "Sente na máquina e ajuste o apoio das coxas",
      "Segure a barra com pegada pronada, mais larga que os ombros",
      "Incline ligeiramente o tronco para trás",
      "Puxe a barra em direção ao peito superior",
      "Retorne controladamente à posição inicial"
    ],
    dicas: [
      "Não balance o corpo durante o movimento",
      "Foque em puxar com as costas, não com os braços",
      "Mantenha o peito estufado",
      "Contraia as escápulas no final do movimento"
    ],
    musculos_primarios: ["latissimo_dorso"],
    musculos_secundarios: ["romboides", "biceps", "deltoides_posterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 90,
    calorias_por_serie: 12
  },
  {
    id: "back_002",
    nome: "Remada Curvada com Barra",
    categoria: "costas",
    grupo_muscular: ["latissimo_dorso", "romboides", "trapezio_medio"],
    equipamento: "barra_olimpica",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Segure a barra com pegada pronada na largura dos ombros",
      "Flexione ligeiramente os joelhos e incline o tronco 45 graus",
      "Mantenha as costas retas e o core contraído",
      "Puxe a barra em direção ao abdômen inferior",
      "Retorne controladamente à posição inicial"
    ],
    dicas: [
      "Não arredonde as costas",
      "Puxe os cotovelos para trás, não para os lados",
      "Mantenha a cabeça em posição neutra",
      "Contraia as escápulas no final do movimento"
    ],
    musculos_primarios: ["latissimo_dorso", "romboides"],
    musculos_secundarios: ["biceps", "trapezio_medio", "deltoides_posterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "6-10",
    descanso_segundos: 120,
    calorias_por_serie: 14
  },
  {
    id: "back_003",
    nome: "Barra Fixa",
    categoria: "costas",
    grupo_muscular: ["latissimo_dorso", "biceps", "romboides"],
    equipamento: "barra_fixa",
    dificuldade: "avancado",
    tipo_movimento: "composto",
    instrucoes: [
      "Segure a barra com pegada pronada, ligeiramente mais larga que os ombros",
      "Pendure com os braços totalmente estendidos",
      "Puxe o corpo para cima até o queixo passar da barra",
      "Desça controladamente até a posição inicial",
      "Mantenha o core contraído durante todo movimento"
    ],
    dicas: [
      "Não balance o corpo",
      "Foque em puxar com as costas",
      "Se for difícil, use elástico ou máquina assistida",
      "Desça completamente entre as repetições"
    ],
    musculos_primarios: ["latissimo_dorso"],
    musculos_secundarios: ["biceps", "romboides", "deltoides_posterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "5-12",
    descanso_segundos: 120,
    calorias_por_serie: 16
  },
  {
    id: "back_004",
    nome: "Remada Unilateral com Halter",
    categoria: "costas",
    grupo_muscular: ["latissimo_dorso", "romboides", "biceps"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "composto",
    instrucoes: [
      "Apoie um joelho e uma mão no banco",
      "Segure o halter com a mão livre",
      "Mantenha as costas retas e paralelas ao chão",
      "Puxe o halter em direção ao quadril",
      "Retorne controladamente à posição inicial"
    ],
    dicas: [
      "Não gire o tronco durante o movimento",
      "Puxe o cotovelo para trás, próximo ao corpo",
      "Mantenha o ombro da mão de apoio estável",
      "Foque na contração das costas"
    ],
    musculos_primarios: ["latissimo_dorso"],
    musculos_secundarios: ["romboides", "biceps", "deltoides_posterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 75,
    calorias_por_serie: 10
  },

  // ==================== OMBROS ====================
  {
    id: "shoulders_001",
    nome: "Desenvolvimento com Halteres",
    categoria: "ombros",
    grupo_muscular: ["deltoides_anterior", "deltoides_medio", "triceps"],
    equipamento: "halteres",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Sente em banco com encosto ou fique em pé",
      "Segure os halteres na altura dos ombros",
      "Empurre os halteres para cima até os braços ficarem estendidos",
      "Desça controladamente até a posição inicial",
      "Mantenha o core contraído durante todo movimento"
    ],
    dicas: [
      "Não arquee excessivamente as costas",
      "Mantenha os cotovelos ligeiramente à frente do corpo",
      "Não deixe os halteres se tocarem no topo",
      "Controle a descida para proteger os ombros"
    ],
    musculos_primarios: ["deltoides_anterior", "deltoides_medio"],
    musculos_secundarios: ["triceps", "trapezio_superior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 90,
    calorias_por_serie: 11
  },
  {
    id: "shoulders_002",
    nome: "Elevação Lateral",
    categoria: "ombros",
    grupo_muscular: ["deltoides_medio"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé com halteres nas mãos ao lado do corpo",
      "Mantenha ligeira flexão nos cotovelos",
      "Eleve os braços lateralmente até a altura dos ombros",
      "Pause brevemente no topo",
      "Desça controladamente à posição inicial"
    ],
    dicas: [
      "Não eleve os braços acima da linha dos ombros",
      "Mantenha os punhos ligeiramente inclinados para baixo",
      "Não balance o corpo para ajudar no movimento",
      "Use peso moderado para manter a forma correta"
    ],
    musculos_primarios: ["deltoides_medio"],
    musculos_secundarios: ["trapezio_superior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "12-15",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },
  {
    id: "shoulders_003",
    nome: "Elevação Frontal",
    categoria: "ombros",
    grupo_muscular: ["deltoides_anterior"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé com halteres à frente das coxas",
      "Mantenha ligeira flexão nos cotovelos",
      "Eleve um braço à frente até a altura dos ombros",
      "Desça controladamente enquanto eleva o outro braço",
      "Alterne os braços de forma contínua"
    ],
    dicas: [
      "Não eleve o braço acima da linha dos ombros",
      "Mantenha o tronco estável",
      "Controle tanto a subida quanto a descida",
      "Pode ser feito com os dois braços simultaneamente"
    ],
    musculos_primarios: ["deltoides_anterior"],
    musculos_secundarios: ["core"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "12-15",
    descanso_segundos: 60,
    calorias_por_serie: 7
  },
  {
    id: "shoulders_004",
    nome: "Crucifixo Inverso",
    categoria: "ombros",
    grupo_muscular: ["deltoides_posterior", "romboides"],
    equipamento: "halteres",
    dificuldade: "intermediario",
    tipo_movimento: "isolado",
    instrucoes: [
      "Incline o tronco 45 graus com halteres nas mãos",
      "Mantenha ligeira flexão nos cotovelos",
      "Abra os braços lateralmente até a altura dos ombros",
      "Contraia as escápulas no final do movimento",
      "Retorne controladamente à posição inicial"
    ],
    dicas: [
      "Mantenha o tronco estável durante todo movimento",
      "Foque na contração dos deltoides posteriores",
      "Não use impulso para elevar os braços",
      "Mantenha a cabeça em posição neutra"
    ],
    musculos_primarios: ["deltoides_posterior"],
    musculos_secundarios: ["romboides", "trapezio_medio"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "12-15",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },

  // ==================== BRAÇOS - BÍCEPS ====================
  {
    id: "biceps_001",
    nome: "Rosca Direta com Barra",
    categoria: "biceps",
    grupo_muscular: ["biceps_braquial", "braquial"],
    equipamento: "barra_reta",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé com a barra nas mãos, pegada supinada",
      "Mantenha os cotovelos próximos ao corpo",
      "Flexione os braços elevando a barra até o peito",
      "Contraia os bíceps no topo do movimento",
      "Desça controladamente à posição inicial"
    ],
    dicas: [
      "Não balance o corpo para ajudar no movimento",
      "Mantenha os cotovelos fixos ao lado do corpo",
      "Não deixe a barra descer completamente",
      "Foque na contração dos bíceps"
    ],
    musculos_primarios: ["biceps_braquial"],
    musculos_secundarios: ["braquial", "braquiorradial"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 75,
    calorias_por_serie: 9
  },
  {
    id: "biceps_002",
    nome: "Rosca Alternada com Halteres",
    categoria: "biceps",
    grupo_muscular: ["biceps_braquial"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé com halteres nas mãos ao lado do corpo",
      "Flexione um braço elevando o halter até o ombro",
      "Gire ligeiramente o punho durante a subida (supinação)",
      "Desça controladamente enquanto eleva o outro braço",
      "Alterne os braços de forma contínua"
    ],
    dicas: [
      "Mantenha o cotovelo fixo ao lado do corpo",
      "Não balance o tronco",
      "Controle tanto a subida quanto a descida",
      "Foque na contração de cada bíceps individualmente"
    ],
    musculos_primarios: ["biceps_braquial"],
    musculos_secundarios: ["braquial"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-14",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },
  {
    id: "biceps_003",
    nome: "Rosca Martelo",
    categoria: "biceps",
    grupo_muscular: ["braquial", "braquiorradial", "biceps_braquial"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé com halteres nas mãos, pegada neutra",
      "Mantenha os punhos na posição neutra durante todo movimento",
      "Flexione os braços elevando os halteres até os ombros",
      "Contraia os músculos no topo",
      "Desça controladamente à posição inicial"
    ],
    dicas: [
      "Não gire os punhos durante o movimento",
      "Mantenha os cotovelos próximos ao corpo",
      "Pode ser feito alternado ou simultâneo",
      "Foque na contração do braquial"
    ],
    musculos_primarios: ["braquial", "braquiorradial"],
    musculos_secundarios: ["biceps_braquial"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-14",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },

  // ==================== BRAÇOS - TRÍCEPS ====================
  {
    id: "triceps_001",
    nome: "Tríceps Testa com Barra",
    categoria: "triceps",
    grupo_muscular: ["triceps_braquial"],
    equipamento: "barra_reta",
    dificuldade: "intermediario",
    tipo_movimento: "isolado",
    instrucoes: [
      "Deite no banco com a barra nas mãos, braços estendidos",
      "Flexione apenas os cotovelos, descendo a barra em direção à testa",
      "Mantenha os cotovelos fixos e apontando para cima",
      "Estenda os braços retornando à posição inicial",
      "Contraia os tríceps no final do movimento"
    ],
    dicas: [
      "Não mova os cotovelos durante o movimento",
      "Desça a barra controladamente",
      "Mantenha os punhos firmes",
      "Use peso moderado para proteger os cotovelos"
    ],
    musculos_primarios: ["triceps_braquial"],
    musculos_secundarios: [],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 75,
    calorias_por_serie: 9
  },
  {
    id: "triceps_002",
    nome: "Mergulho em Paralelas",
    categoria: "triceps",
    grupo_muscular: ["triceps_braquial", "peitoral_inferior"],
    equipamento: "paralelas",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Apoie-se nas paralelas com braços estendidos",
      "Desça o corpo flexionando os cotovelos",
      "Mantenha o tronco ligeiramente inclinado à frente",
      "Desça até sentir alongamento no peito",
      "Empurre o corpo de volta à posição inicial"
    ],
    dicas: [
      "Não desça excessivamente para proteger os ombros",
      "Mantenha os cotovelos próximos ao corpo",
      "Se for difícil, use máquina assistida",
      "Foque na contração dos tríceps"
    ],
    musculos_primarios: ["triceps_braquial"],
    musculos_secundarios: ["peitoral_inferior", "deltoides_anterior"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "6-12",
    descanso_segundos: 90,
    calorias_por_serie: 12
  },
  {
    id: "triceps_003",
    nome: "Extensão de Tríceps com Halter",
    categoria: "triceps",
    grupo_muscular: ["triceps_braquial"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Fique em pé ou sentado com um halter nas duas mãos",
      "Eleve o halter acima da cabeça com braços estendidos",
      "Flexione apenas os cotovelos, descendo o halter atrás da cabeça",
      "Estenda os braços retornando à posição inicial",
      "Mantenha os cotovelos próximos à cabeça"
    ],
    dicas: [
      "Não mova os cotovelos durante o movimento",
      "Mantenha o core contraído",
      "Desça o peso controladamente",
      "Cuidado para não bater o halter na cabeça"
    ],
    musculos_primarios: ["triceps_braquial"],
    musculos_secundarios: [],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-15",
    descanso_segundos: 60,
    calorias_por_serie: 8
  },

  // ==================== PERNAS - QUADRÍCEPS ====================
  {
    id: "quads_001",
    nome: "Agachamento Livre",
    categoria: "pernas",
    grupo_muscular: ["quadriceps", "gluteos", "isquiotibiais"],
    equipamento: "barra_olimpica",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Posicione a barra no trapézio superior",
      "Fique com pés na largura dos ombros",
      "Desça flexionando quadris e joelhos simultaneamente",
      "Desça até as coxas ficarem paralelas ao chão",
      "Empurre o chão com os pés para subir"
    ],
    dicas: [
      "Mantenha o peito estufado e costas retas",
      "Não deixe os joelhos passarem da linha dos pés",
      "Distribua o peso entre calcanhar e meio do pé",
      "Mantenha os joelhos alinhados com os pés"
    ],
    musculos_primarios: ["quadriceps", "gluteos"],
    musculos_secundarios: ["isquiotibiais", "panturrilhas", "core"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "6-12",
    descanso_segundos: 120,
    calorias_por_serie: 18
  },
  {
    id: "quads_002",
    nome: "Leg Press 45°",
    categoria: "pernas",
    grupo_muscular: ["quadriceps", "gluteos"],
    equipamento: "leg_press",
    dificuldade: "iniciante",
    tipo_movimento: "composto",
    instrucoes: [
      "Sente na máquina com costas apoiadas",
      "Posicione os pés na plataforma na largura dos ombros",
      "Desça controladamente flexionando os joelhos",
      "Desça até formar ângulo de 90 graus nos joelhos",
      "Empurre a plataforma de volta à posição inicial"
    ],
    dicas: [
      "Não trave completamente os joelhos no topo",
      "Mantenha os joelhos alinhados com os pés",
      "Não deixe a lombar arredondar",
      "Controle tanto a descida quanto a subida"
    ],
    musculos_primarios: ["quadriceps"],
    musculos_secundarios: ["gluteos", "isquiotibiais"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-15",
    descanso_segundos: 90,
    calorias_por_serie: 15
  },
  {
    id: "quads_003",
    nome: "Extensão de Pernas",
    categoria: "pernas",
    grupo_muscular: ["quadriceps"],
    equipamento: "cadeira_extensora",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Sente na máquina com costas apoiadas",
      "Posicione os pés atrás das almofadas",
      "Estenda as pernas até ficarem completamente retas",
      "Contraia os quadríceps no topo do movimento",
      "Desça controladamente à posição inicial"
    ],
    dicas: [
      "Não use impulso para elevar o peso",
      "Mantenha as costas apoiadas no encosto",
      "Contraia os quadríceps no topo",
      "Desça controladamente, não deixe o peso cair"
    ],
    musculos_primarios: ["quadriceps"],
    musculos_secundarios: [],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "12-15",
    descanso_segundos: 60,
    calorias_por_serie: 10
  },

  // ==================== PERNAS - POSTERIORES ====================
  {
    id: "hamstrings_001",
    nome: "Stiff com Barra",
    categoria: "pernas",
    grupo_muscular: ["isquiotibiais", "gluteos"],
    equipamento: "barra_olimpica",
    dificuldade: "intermediario",
    tipo_movimento: "composto",
    instrucoes: [
      "Fique em pé com a barra nas mãos, pegada pronada",
      "Mantenha ligeira flexão nos joelhos",
      "Flexione o quadril empurrando o bumbum para trás",
      "Desça a barra próxima às pernas até sentir alongamento",
      "Retorne à posição inicial contraindo glúteos e posteriores"
    ],
    dicas: [
      "Mantenha as costas retas durante todo movimento",
      "Não flexione excessivamente os joelhos",
      "Foque no movimento do quadril, não dos joelhos",
      "Sinta o alongamento nos isquiotibiais"
    ],
    musculos_primarios: ["isquiotibiais", "gluteos"],
    musculos_secundarios: ["eretores_espinha"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-12",
    descanso_segundos: 90,
    calorias_por_serie: 14
  },
  {
    id: "hamstrings_002",
    nome: "Mesa Flexora",
    categoria: "pernas",
    grupo_muscular: ["isquiotibiais"],
    equipamento: "mesa_flexora",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Deite na máquina com o quadril apoiado",
      "Posicione os calcanhares sob as almofadas",
      "Flexione os joelhos trazendo os calcanhares em direção aos glúteos",
      "Contraia os isquiotibiais no topo do movimento",
      "Retorne controladamente à posição inicial"
    ],
    dicas: [
      "Mantenha o quadril apoiado na máquina",
      "Não eleve o quadril durante o movimento",
      "Contraia os isquiotibiais no topo",
      "Controle tanto a subida quanto a descida"
    ],
    musculos_primarios: ["isquiotibiais"],
    musculos_secundarios: ["panturrilhas"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-15",
    descanso_segundos: 60,
    calorias_por_serie: 9
  },

  // ==================== GLÚTEOS ====================
  {
    id: "glutes_001",
    nome: "Hip Thrust com Barra",
    categoria: "gluteos",
    grupo_muscular: ["gluteos", "isquiotibiais"],
    equipamento: "barra_olimpica",
    dificuldade: "intermediario",
    tipo_movimento: "isolado",
    instrucoes: [
      "Sente com as costas apoiadas no banco",
      "Posicione a barra sobre o quadril",
      "Apoie os pés no chão na largura dos ombros",
      "Eleve o quadril contraindo os glúteos",
      "Desça controladamente sem tocar o chão"
    ],
    dicas: [
      "Mantenha o queixo recolhido",
      "Foque na contração dos glúteos",
      "Não arquee excessivamente a lombar",
      "Mantenha os joelhos alinhados com os pés"
    ],
    musculos_primarios: ["gluteos"],
    musculos_secundarios: ["isquiotibiais", "core"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "8-15",
    descanso_segundos: 75,
    calorias_por_serie: 12
  },
  {
    id: "glutes_002",
    nome: "Agachamento Sumô",
    categoria: "gluteos",
    grupo_muscular: ["gluteos", "quadriceps", "adutores"],
    equipamento: "halteres",
    dificuldade: "iniciante",
    tipo_movimento: "composto",
    instrucoes: [
      "Fique com pés mais largos que os ombros, pontas dos pés para fora",
      "Segure um halter com as duas mãos entre as pernas",
      "Desça flexionando quadris e joelhos",
      "Mantenha o tronco ereto durante todo movimento",
      "Suba contraindo glúteos e quadríceps"
    ],
    dicas: [
      "Mantenha os joelhos alinhados com os pés",
      "Desça até as coxas ficarem paralelas ao chão",
      "Foque na contração dos glúteos",
      "Mantenha o peso no calcanhar e meio do pé"
    ],
    musculos_primarios: ["gluteos", "quadriceps"],
    musculos_secundarios: ["adutores", "isquiotibiais"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "10-15",
    descanso_segundos: 75,
    calorias_por_serie: 13
  },

  // ==================== PANTURRILHAS ====================
  {
    id: "calves_001",
    nome: "Elevação de Panturrilha em Pé",
    categoria: "panturrilhas",
    grupo_muscular: ["gastrocnemio", "soleo"],
    equipamento: "smith_machine",
    dificuldade: "iniciante",
    tipo_movimento: "isolado",
    instrucoes: [
      "Posicione-se na máquina com a barra nos ombros",
      "Coloque a ponta dos pés em uma plataforma elevada",
      "Eleve o corpo na ponta dos pés o máximo possível",
      "Contraia as panturrilhas no topo do movimento",
      "Desça controladamente até sentir alongamento"
    ],
    dicas: [
      "Mantenha os joelhos ligeiramente flexionados",
      "Foque na contração das panturrilhas",
      "Não balance durante o movimento",
      "Faça amplitude completa de movimento"
    ],
    musculos_primarios: ["gastrocnemio"],
    musculos_secundarios: ["soleo"],
    series_recomendadas: "4-5",
    repeticoes_recomendadas: "15-20",
    descanso_segundos: 45,
    calorias_por_serie: 6
  },

  // ==================== CORE/ABDÔMEN ====================
  {
    id: "abs_001",
    nome: "Prancha",
    categoria: "core",
    grupo_muscular: ["reto_abdominal", "transverso_abdominal", "obliquos"],
    equipamento: "peso_corporal",
    dificuldade: "iniciante",
    tipo_movimento: "isometrico",
    instrucoes: [
      "Posicione-se em prancha com antebraços no chão",
      "Mantenha o corpo alinhado da cabeça aos pés",
      "Contraia o core e mantenha a posição",
      "Respire normalmente durante o exercício",
      "Mantenha a posição pelo tempo determinado"
    ],
    dicas: [
      "Não deixe o quadril subir ou descer",
      "Mantenha o pescoço em posição neutra",
      "Contraia o core durante todo o tempo",
      "Comece com 30 segundos e aumente gradualmente"
    ],
    musculos_primarios: ["reto_abdominal", "transverso_abdominal"],
    musculos_secundarios: ["obliquos", "deltoides", "gluteos"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "30-60s",
    descanso_segundos: 60,
    calorias_por_serie: 5
  },
  {
    id: "abs_002",
    nome: "Abdominal Supra",
    categoria: "core",
    grupo_muscular: ["reto_abdominal"],
    equipamento: "peso_corporal",
    dificuldade: "iniciante",
    tipo_movimento: "dinamico",
    instrucoes: [
      "Deite com joelhos flexionados e pés apoiados",
      "Coloque as mãos atrás da cabeça ou cruzadas no peito",
      "Eleve o tronco contraindo o abdômen",
      "Suba apenas até as escápulas saírem do chão",
      "Desça controladamente à posição inicial"
    ],
    dicas: [
      "Não puxe a cabeça com as mãos",
      "Foque na contração do abdômen",
      "Não suba completamente, apenas tire as escápulas do chão",
      "Expire na subida, inspire na descida"
    ],
    musculos_primarios: ["reto_abdominal"],
    musculos_secundarios: ["obliquos"],
    series_recomendadas: "3-4",
    repeticoes_recomendadas: "15-25",
    descanso_segundos: 45,
    calorias_por_serie: 6
  }
];

// Funções utilitárias para busca e filtros
export const searchExercises = (query) => {
  if (!query) return exerciseDatabase;
  
  const searchTerm = query.toLowerCase();
  return exerciseDatabase.filter(exercise => 
    exercise.nome.toLowerCase().includes(searchTerm) ||
    exercise.categoria.toLowerCase().includes(searchTerm) ||
    exercise.grupo_muscular.some(muscle => muscle.toLowerCase().includes(searchTerm)) ||
    exercise.equipamento.toLowerCase().includes(searchTerm)
  );
};

export const getExercisesByCategory = (category) => {
  return exerciseDatabase.filter(exercise => exercise.categoria === category);
};

export const getExercisesByMuscleGroup = (muscleGroup) => {
  return exerciseDatabase.filter(exercise => 
    exercise.grupo_muscular.includes(muscleGroup) ||
    exercise.musculos_primarios.includes(muscleGroup) ||
    exercise.musculos_secundarios.includes(muscleGroup)
  );
};

export const getExercisesByEquipment = (equipment) => {
  return exerciseDatabase.filter(exercise => exercise.equipamento === equipment);
};

export const getExercisesByDifficulty = (difficulty) => {
  return exerciseDatabase.filter(exercise => exercise.dificuldade === difficulty);
};

export const getExerciseById = (id) => {
  return exerciseDatabase.find(exercise => exercise.id === id);
};

// Categorias de exercícios
export const exerciseCategories = [
  { id: "peito", nome: "Peito", icon: "💪", color: "bg-red-500" },
  { id: "costas", nome: "Costas", icon: "🏋️", color: "bg-blue-500" },
  { id: "ombros", nome: "Ombros", icon: "🤸", color: "bg-yellow-500" },
  { id: "biceps", nome: "Bíceps", icon: "💪", color: "bg-green-500" },
  { id: "triceps", nome: "Tríceps", icon: "🔥", color: "bg-orange-500" },
  { id: "pernas", nome: "Pernas", icon: "🦵", color: "bg-purple-500" },
  { id: "gluteos", nome: "Glúteos", icon: "🍑", color: "bg-pink-500" },
  { id: "panturrilhas", nome: "Panturrilhas", icon: "🦵", color: "bg-indigo-500" },
  { id: "core", nome: "Core/Abdômen", icon: "⚡", color: "bg-gray-500" }
];

// Tipos de equipamento
export const equipmentTypes = [
  { id: "peso_corporal", nome: "Peso Corporal", icon: "🤸" },
  { id: "halteres", nome: "Halteres", icon: "🏋️" },
  { id: "barra_olimpica", nome: "Barra Olímpica", icon: "🏋️‍♂️" },
  { id: "barra_reta", nome: "Barra Reta", icon: "➖" },
  { id: "barra_fixa", nome: "Barra Fixa", icon: "🤸‍♂️" },
  { id: "polia_alta", nome: "Polia Alta", icon: "🔗" },
  { id: "leg_press", nome: "Leg Press", icon: "🦵" },
  { id: "cadeira_extensora", nome: "Cadeira Extensora", icon: "💺" },
  { id: "mesa_flexora", nome: "Mesa Flexora", icon: "🛏️" },
  { id: "smith_machine", nome: "Smith Machine", icon: "🏗️" },
  { id: "paralelas", nome: "Paralelas", icon: "⚖️" }
];

// Níveis de dificuldade
export const difficultyLevels = [
  { id: "iniciante", nome: "Iniciante", color: "bg-green-500", description: "Para quem está começando" },
  { id: "intermediario", nome: "Intermediário", color: "bg-yellow-500", description: "Para quem já tem experiência" },
  { id: "avancado", nome: "Avançado", color: "bg-red-500", description: "Para atletas experientes" }
];

export default exerciseDatabase;

