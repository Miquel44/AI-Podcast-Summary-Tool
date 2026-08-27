export type Lang = 'es' | 'en' | 'ca'

export const LANGS: Lang[] = ['es', 'en', 'ca']

export interface Strings {
  interests: string
  dashboard: string
  home: string
  featured: string
  listen: string
  generate: string
  refresh: string
  refreshing: string
  preparing: string
  emptyTitle: string
  emptySub: string
  chipGenerating: string
  chipReady: string
  chipFailed: string
  modalGenerating: string
  modalRetry: string
  modalRegenerate: string
  sources: string
  scriptLabel: string
  oneVoice: string
  dialogue: string
  min: string
  loading: string
  close: string
  langWarning: string
  // Interests modal
  intTitle: string
  intSubtitle: string
  intRecommended: string
  intRecommendedHint: string
  intExtra: string
  intDescribe: string
  intPlaceholder: string
  intAnalyze: string
  intAnalyzing: string
  intAudio: string
  intApply: string
  intApplying: string
  intCostWarning: string
  // Dashboard
  dashTitle: string
  dashSubtitle: string
  dashMau: string
  dashStickiness: string
  dashMinListen: string
  dashListenThrough: string
  dashCostEpisode: string
  dashCostListener: string
  dashMargin: string
  dashCostTotal: string
  dashDau: string
  dashDailyCost: string
  dashCostPerListener: string
  dashListensByCat: string
  dashReal: string
  dashRealHint: string
  dashLlm: string
  dashTts: string
  dashCalls: string
  dashTokens: string
  dashChars: string
  dashRealEpisodes: string
  dashRealAvgMin: string
  dashMockNote: string
  dashPaid: string
  dashPlaysDay: string
  dashListenersDay: string
  dashEngaged: string
  dashCompletion: string
  dashPeakHour: string
  dashCostGeneration: string
  dashCostUserDay: string
  dashSavingsReuse: string
  dashRetention: string
  dashHourly: string
  dashGenVsReuse: string
  dashGenerated: string
  dashReused: string
  dashTopEpisodes: string
  dashPlaysCol: string
  dashCompletionCol: string
  dashCohorts: string
  dashCohortUsers: string
  dashWeekAbbr: string
  dashTabGeneral: string
  dashTabTopics: string
  dashTabEpisodes: string
  dashRetentionGeneral: string
  dashEpisodeSelect: string
  dashListeners: string
  dashDaySince: string
  dashCostByCat: string
  dashDuration: string
  dashReplay: string
  dashSkipped: string
  dashAnalyze: string
  dashAnalyzing: string
  dashAnalysis: string
  dashRecommendation: string
  searchPlaceholder: string
  searchEmpty: string
  markReplay: string
  markSkip: string
}

export const STRINGS: Record<Lang, Strings> = {
  es: {
    interests: 'Mis intereses',
    dashboard: 'Dashboard',
    home: 'Inicio',
    featured: 'Historia destacada',
    listen: '▶ Escuchar episodio',
    generate: '▶ Generar episodio',
    refresh: '⟳ Actualizar',
    refreshing: '⟳ Actualizando…',
    preparing: 'Preparando la edición de hoy…',
    emptyTitle: 'Tu emisora personal',
    emptySub: 'Primera ejecución: estamos poblando las noticias de hoy (≈1 minuto). Las historias irán apareciendo solas.',
    chipGenerating: '● Generando…',
    chipReady: '▶ Listo',
    chipFailed: '⚠ Error',
    modalGenerating: '⟳ Generando episodio… (guion + voces, ~1-2 min)',
    modalRetry: 'Reintentar generación',
    modalRegenerate: '↻ Regenerar con el estilo actual',
    sources: 'Fuentes',
    scriptLabel: 'Transcripción',
    oneVoice: 'Una voz',
    dialogue: 'Diálogo',
    min: 'min',
    loading: 'Cargando…',
    close: 'Cerrar',
    langWarning:
      'Cambiar el idioma muestra la edición en ese idioma. Si aún no existe o está desactualizada, se generará ahora (con coste de API en esta demo); las ediciones y episodios ya creados se conservan. ¿Continuar?',
    intTitle: 'Tus intereses',
    intSubtitle: 'Elige de qué temas quieres podcasts. También puedes describirlos con tus palabras o con un audio.',
    intRecommended: 'Recomendados',
    intRecommendedHint: 'Ya tienen episodios generados',
    intExtra: 'Más temas',
    intDescribe: 'Cuéntamelo tú',
    intPlaceholder: 'P. ej.: me interesa la escalada, la historia naval y todo lo que haga Nvidia…',
    intAnalyze: 'Extraer temas del texto',
    intAnalyzing: 'Analizando…',
    intAudio: 'O sube un audio',
    intApply: 'Guardar intereses',
    intApplying: 'Guardando…',
    intCostWarning:
      'Has elegido temas nuevos sin episodios pregenerados. Al guardarlos se buscarán noticias y se generarán guiones nuevos (coste de API en esta demo). ¿Continuar?',
    dashTitle: 'Dashboard interno',
    dashSubtitle: 'Métricas de uso · últimos 60 días · datos simulados salvo el panel "En vivo"',
    dashMau: 'Usuarios activos (MAU)',
    dashStickiness: 'DAU/MAU',
    dashMinListen: 'Min. por escucha',
    dashListenThrough: 'Escucha completa',
    dashCostEpisode: 'Coste por episodio',
    dashCostListener: 'Coste por oyente/mes',
    dashMargin: 'Margen bruto (4,99 €/mes)',
    dashCostTotal: 'Coste total (60 d)',
    dashDau: 'Oyentes activos diarios',
    dashDailyCost: 'Coste diario de generación',
    dashCostPerListener: 'Coste por oyente activo (mensualizado)',
    dashListensByCat: 'Escuchas por categoría (60 d)',
    dashReal: 'En vivo — esta instancia',
    dashRealHint: 'Medido de verdad en la base de datos local (ledger de llamadas API)',
    dashLlm: 'LLM',
    dashTts: 'Voz (TTS)',
    dashCalls: 'llamadas',
    dashTokens: 'tokens',
    dashChars: 'caracteres',
    dashRealEpisodes: 'Episodios generados',
    dashRealAvgMin: 'Duración media',
    dashMockNote: 'Las ediciones diarias son compartidas: un episodio se genera UNA vez y lo escuchan todos. Los episodios aún relevantes se reutilizan del día anterior sin regenerar. El coste crece con el contenido, no con los usuarios — solo lo custom (de pago) genera coste por usuario.',
    dashPaid: 'Usuarios de pago',
    dashPlaysDay: 'Plays/día (≥30s)',
    dashListenersDay: 'Oyentes únicos/día',
    dashEngaged: 'Engaged (≥40% ep.)',
    dashCompletion: 'Escucha completa',
    dashPeakHour: 'Hora pico de escucha',
    dashCostGeneration: 'Coste por generación',
    dashCostUserDay: 'Coste diario por usuario',
    dashSavingsReuse: 'Ahorro por reutilización (60 d)',
    dashRetention: 'Retención del episodio',
    dashHourly: 'Escuchas por hora del día',
    dashGenVsReuse: 'Episodios: generados vs reutilizados',
    dashGenerated: 'Generados',
    dashReused: 'Reutilizados',
    dashTopEpisodes: 'Top episodios (7 d)',
    dashPlaysCol: 'Plays',
    dashCompletionCol: 'Completado',
    dashCohorts: 'Retención por cohortes semanales',
    dashCohortUsers: 'Altas',
    dashWeekAbbr: 'S',
    dashTabGeneral: 'General',
    dashTabTopics: 'Por temática',
    dashTabEpisodes: 'Por episodio',
    dashRetentionGeneral: 'Retención media global — ¿fatiga del formato?',
    dashEpisodeSelect: 'Episodio',
    dashListeners: 'Oyentes únicos',
    dashDaySince: 'Plays por día desde publicación',
    dashCostByCat: 'Coste por episodio por categoría',
    dashDuration: 'Duración',
    dashReplay: 'Momento más repetido',
    dashSkipped: 'Momento más saltado',
    dashAnalyze: '✦ Analizar este episodio con IA',
    dashAnalyzing: '✦ Analizando estadísticas…',
    dashAnalysis: 'Análisis del episodio (GPT-5.6 Sol)',
    dashRecommendation: 'Recomendación',
    searchPlaceholder: 'Buscar podcasts…',
    searchEmpty: 'Sin resultados para',
    markReplay: '▲ más repetido',
    markSkip: '▼ más saltado',
  },
  en: {
    interests: 'My interests',
    dashboard: 'Dashboard',
    home: 'Home',
    featured: 'Featured story',
    listen: '▶ Listen to episode',
    generate: '▶ Generate episode',
    refresh: '⟳ Refresh',
    refreshing: '⟳ Refreshing…',
    preparing: 'Preparing today’s edition…',
    emptyTitle: 'Your personal station',
    emptySub: 'First run: populating today’s news (≈1 minute). Stories will appear on their own.',
    chipGenerating: '● Generating…',
    chipReady: '▶ Ready',
    chipFailed: '⚠ Error',
    modalGenerating: '⟳ Generating episode… (script + voices, ~1-2 min)',
    modalRetry: 'Retry generation',
    modalRegenerate: '↻ Regenerate with current style',
    sources: 'Sources',
    scriptLabel: 'Transcript',
    oneVoice: 'One voice',
    dialogue: 'Dialogue',
    min: 'min',
    loading: 'Loading…',
    close: 'Close',
    langWarning:
      'Switching shows the edition in that language. If it does not exist yet or is stale, it will be generated now (API cost in this demo); already-created editions and episodes are kept. Continue?',
    intTitle: 'Your interests',
    intSubtitle: 'Pick the topics you want podcasts about. You can also describe them in your own words or with an audio note.',
    intRecommended: 'Recommended',
    intRecommendedHint: 'Already have generated episodes',
    intExtra: 'More topics',
    intDescribe: 'Tell me yourself',
    intPlaceholder: 'E.g.: I care about climbing, naval history and everything Nvidia does…',
    intAnalyze: 'Extract topics from text',
    intAnalyzing: 'Analyzing…',
    intAudio: 'Or upload an audio note',
    intApply: 'Save interests',
    intApplying: 'Saving…',
    intCostWarning:
      'You selected new topics with no pre-generated episodes. Saving will fetch news and generate new scripts (API cost in this demo). Continue?',
    dashTitle: 'Internal dashboard',
    dashSubtitle: 'Usage metrics · last 60 days · simulated data except the "Live" panel',
    dashMau: 'Active users (MAU)',
    dashStickiness: 'DAU/MAU',
    dashMinListen: 'Min. per listen',
    dashListenThrough: 'Listen-through',
    dashCostEpisode: 'Cost per episode',
    dashCostListener: 'Cost per listener/mo',
    dashMargin: 'Gross margin (€4.99/mo)',
    dashCostTotal: 'Total cost (60 d)',
    dashDau: 'Daily active listeners',
    dashDailyCost: 'Daily generation cost',
    dashCostPerListener: 'Cost per active listener (monthly)',
    dashListensByCat: 'Listens by category (60 d)',
    dashReal: 'Live — this instance',
    dashRealHint: 'Actually measured in the local database (API call ledger)',
    dashLlm: 'LLM',
    dashTts: 'Voice (TTS)',
    dashCalls: 'calls',
    dashTokens: 'tokens',
    dashChars: 'characters',
    dashRealEpisodes: 'Episodes generated',
    dashRealAvgMin: 'Avg. duration',
    dashMockNote: 'Daily editions are shared: an episode is generated ONCE and everyone listens to it. Episodes still relevant are reused from the previous day without regenerating. Cost scales with content, not users — only custom (paid) episodes add per-user cost.',
    dashPaid: 'Paying users',
    dashPlaysDay: 'Plays/day (≥30s)',
    dashListenersDay: 'Unique listeners/day',
    dashEngaged: 'Engaged (≥40% ep.)',
    dashCompletion: 'Listen-through',
    dashPeakHour: 'Peak listening hour',
    dashCostGeneration: 'Cost per generation',
    dashCostUserDay: 'Daily cost per user',
    dashSavingsReuse: 'Savings from reuse (60 d)',
    dashRetention: 'Episode retention',
    dashHourly: 'Plays by hour of day',
    dashGenVsReuse: 'Episodes: generated vs reused',
    dashGenerated: 'Generated',
    dashReused: 'Reused',
    dashTopEpisodes: 'Top episodes (7 d)',
    dashPlaysCol: 'Plays',
    dashCompletionCol: 'Completion',
    dashCohorts: 'Weekly cohort retention',
    dashCohortUsers: 'Signups',
    dashWeekAbbr: 'W',
    dashTabGeneral: 'General',
    dashTabTopics: 'By topic',
    dashTabEpisodes: 'By episode',
    dashRetentionGeneral: 'Global avg. retention — format fatigue?',
    dashEpisodeSelect: 'Episode',
    dashListeners: 'Unique listeners',
    dashDaySince: 'Plays by day since publish',
    dashCostByCat: 'Cost per episode by category',
    dashDuration: 'Duration',
    dashReplay: 'Most replayed moment',
    dashSkipped: 'Most skipped moment',
    dashAnalyze: '✦ Analyze this episode with AI',
    dashAnalyzing: '✦ Analyzing stats…',
    dashAnalysis: 'Episode analysis (GPT-5.6 Sol)',
    dashRecommendation: 'Recommendation',
    searchPlaceholder: 'Search podcasts…',
    searchEmpty: 'No results for',
    markReplay: '▲ most replayed',
    markSkip: '▼ most skipped',
  },
  ca: {
    interests: 'Els meus interessos',
    dashboard: 'Dashboard',
    home: 'Inici',
    featured: 'Història destacada',
    listen: '▶ Escoltar episodi',
    generate: '▶ Generar episodi',
    refresh: '⟳ Actualitzar',
    refreshing: '⟳ Actualitzant…',
    preparing: 'Preparant l’edició d’avui…',
    emptyTitle: 'La teva emissora personal',
    emptySub: 'Primera execució: estem poblant les notícies d’avui (≈1 minut). Les històries aniran apareixent soles.',
    chipGenerating: '● Generant…',
    chipReady: '▶ A punt',
    chipFailed: '⚠ Error',
    modalGenerating: '⟳ Generant episodi… (guió + veus, ~1-2 min)',
    modalRetry: 'Reintentar generació',
    modalRegenerate: '↻ Regenerar amb l’estil actual',
    sources: 'Fonts',
    scriptLabel: 'Transcripció',
    oneVoice: 'Una veu',
    dialogue: 'Diàleg',
    min: 'min',
    loading: 'Carregant…',
    close: 'Tancar',
    langWarning:
      'Canviar mostra l’edició en aquell idioma. Si encara no existeix o està desactualitzada, es generarà ara (cost d’API en aquesta demo); les edicions i episodis ja creats es conserven. Continuar?',
    intTitle: 'Els teus interessos',
    intSubtitle: 'Tria els temes dels quals vols podcasts. També pots descriure’ls amb les teves paraules o amb un àudio.',
    intRecommended: 'Recomanats',
    intRecommendedHint: 'Ja tenen episodis generats',
    intExtra: 'Més temes',
    intDescribe: 'Explica-m’ho tu',
    intPlaceholder: 'P. ex.: m’interessa l’escalada, la història naval i tot el que faci Nvidia…',
    intAnalyze: 'Extreure temes del text',
    intAnalyzing: 'Analitzant…',
    intAudio: 'O puja un àudio',
    intApply: 'Desar interessos',
    intApplying: 'Desant…',
    intCostWarning:
      'Has triat temes nous sense episodis pregenerats. En desar-los es buscaran notícies i es generaran guions nous (cost d’API en aquesta demo). Continuar?',
    dashTitle: 'Dashboard intern',
    dashSubtitle: 'Mètriques d’ús · últims 60 dies · dades simulades excepte el panell "En viu"',
    dashMau: 'Usuaris actius (MAU)',
    dashStickiness: 'DAU/MAU',
    dashMinListen: 'Min. per escolta',
    dashListenThrough: 'Escolta completa',
    dashCostEpisode: 'Cost per episodi',
    dashCostListener: 'Cost per oient/mes',
    dashMargin: 'Marge brut (4,99 €/mes)',
    dashCostTotal: 'Cost total (60 d)',
    dashDau: 'Oients actius diaris',
    dashDailyCost: 'Cost diari de generació',
    dashCostPerListener: 'Cost per oient actiu (mensualitzat)',
    dashListensByCat: 'Escoltes per categoria (60 d)',
    dashReal: 'En viu — aquesta instància',
    dashRealHint: 'Mesurat de debò a la base de dades local (ledger de crides API)',
    dashLlm: 'LLM',
    dashTts: 'Veu (TTS)',
    dashCalls: 'crides',
    dashTokens: 'tokens',
    dashChars: 'caràcters',
    dashRealEpisodes: 'Episodis generats',
    dashRealAvgMin: 'Durada mitjana',
    dashMockNote: 'Les edicions diàries són compartides: un episodi es genera UNA vegada i l’escolten tots. Els episodis encara rellevants es reutilitzen del dia anterior sense regenerar. El cost creix amb el contingut, no amb els usuaris — només el custom (de pagament) afegeix cost per usuari.',
    dashPaid: 'Usuaris de pagament',
    dashPlaysDay: 'Plays/dia (≥30s)',
    dashListenersDay: 'Oients únics/dia',
    dashEngaged: 'Engaged (≥40% ep.)',
    dashCompletion: 'Escolta completa',
    dashPeakHour: 'Hora punta d’escolta',
    dashCostGeneration: 'Cost per generació',
    dashCostUserDay: 'Cost diari per usuari',
    dashSavingsReuse: 'Estalvi per reutilització (60 d)',
    dashRetention: 'Retenció de l’episodi',
    dashHourly: 'Escoltes per hora del dia',
    dashGenVsReuse: 'Episodis: generats vs reutilitzats',
    dashGenerated: 'Generats',
    dashReused: 'Reutilitzats',
    dashTopEpisodes: 'Top episodis (7 d)',
    dashPlaysCol: 'Plays',
    dashCompletionCol: 'Completat',
    dashCohorts: 'Retenció per cohorts setmanals',
    dashCohortUsers: 'Altes',
    dashWeekAbbr: 'S',
    dashTabGeneral: 'General',
    dashTabTopics: 'Per temàtica',
    dashTabEpisodes: 'Per episodi',
    dashRetentionGeneral: 'Retenció mitjana global — fatiga del format?',
    dashEpisodeSelect: 'Episodi',
    dashListeners: 'Oients únics',
    dashDaySince: 'Plays per dia des de publicació',
    dashCostByCat: 'Cost per episodi per categoria',
    dashDuration: 'Durada',
    dashReplay: 'Moment més repetit',
    dashSkipped: 'Moment més saltat',
    dashAnalyze: '✦ Analitzar aquest episodi amb IA',
    dashAnalyzing: '✦ Analitzant estadístiques…',
    dashAnalysis: 'Anàlisi de l’episodi (GPT-5.6 Sol)',
    dashRecommendation: 'Recomanació',
    searchPlaceholder: 'Cercar podcasts…',
    searchEmpty: 'Sense resultats per a',
    markReplay: '▲ més repetit',
    markSkip: '▼ més saltat',
  },
}
