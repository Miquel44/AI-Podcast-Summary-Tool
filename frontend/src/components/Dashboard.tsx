import { useEffect, useState } from 'react'
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, LabelList, Legend, Line,
  LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import type { Strings } from '../i18n'

// Palette validated with the dataviz six-checks script on surface #14141b.
const SERIES_1 = '#3987e5'
const SERIES_2 = '#d95926'
const GRID = '#2c2c2a'
const MUTED = '#898781'
const SURFACE = '#14141b'

interface DayPoint {
  date: string
  users: number
  paid_users: number
  dau: number
  listeners: number
  plays: number
  minutes: number
  generated: number
  reused: number
  custom: number
  llm_cost: number
  tts_cost: number
}

interface Metrics {
  series: DayPoint[]
  retention: { pct: number; audience: number }[]
  cohorts: { cohort: string; size: number; weeks: number[] }[]
  hourly: { hour: string; plays: number }[]
  per_category: { category: string; listens: number; cost_per_episode: number }[]
  top_episodes: { title: string; category: string; plays: number; completion: number }[]
  kpis: Record<string, number | string>
  real: {
    by_kind: { kind: string; calls: number; cost_usd: number; tokens: number; characters: number }[]
    episodes: number
    avg_episode_minutes: number
  }
}

interface EpisodeStats {
  story_id: number
  title: string
  category: string
  status: string
  duration_s: number | null
  plays: number
  listeners: number
  completion: number
  most_replayed_pct: number
  most_skipped_pct: number
  retention: { pct: number; audience: number }[]
  daily: { day: string; plays: number }[]
}

interface Analysis {
  insights: string[]
  recommendation: string
}

type Tab = 'general' | 'topics' | 'episodes'

const axisProps = {
  stroke: 'none',
  tick: { fill: MUTED, fontSize: 11 },
  tickLine: false,
  axisLine: { stroke: '#383835' },
} as const

const tooltipStyle = {
  contentStyle: {
    background: '#1c1c24',
    border: '1px solid rgba(255,255,255,0.10)',
    borderRadius: 8,
    fontSize: 12,
    color: '#f2efe9',
  },
  labelStyle: { color: MUTED },
} as const

const CHART_DIM = { width: 620, height: 200 }

function shortDate(iso: string) {
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}`
}

function Tile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl bg-ink-soft p-4">
      <p className="text-[11px] tracking-wide text-white/40 uppercase">{label}</p>
      <p className="mt-1.5 font-display text-2xl font-700 text-white">{value}</p>
      {hint && <p className="mt-0.5 text-[11px] text-emerald-400">{hint}</p>}
    </div>
  )
}

function Panel({
  title,
  span,
  children,
}: {
  title: string
  span?: boolean
  children: React.ReactNode
}) {
  return (
    <div className={`rounded-xl bg-ink-soft p-4 ${span ? 'lg:col-span-2' : ''}`}>
      <p className="mb-3 text-[11px] font-semibold tracking-wide text-white/50 uppercase">{title}</p>
      {children}
    </div>
  )
}

function RetentionChart({
  data,
  replayPct,
  skipPct,
  replayLabel = '▲',
  skipLabel = '▼',
}: {
  data: { pct: number; audience: number }[]
  replayPct?: number
  skipPct?: number
  replayLabel?: string
  skipLabel?: string
}) {
  return (
    <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
      <LineChart data={data} margin={{ top: 14, right: 8, bottom: 0, left: -12 }}>
        <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
        <XAxis dataKey="pct" {...axisProps} tickFormatter={(v: number) => `${v}%`} minTickGap={24} />
        <YAxis {...axisProps} domain={[0, 100]} tickFormatter={(v: number) => `${v}%`} />
        <Tooltip {...tooltipStyle} cursor={{ stroke: MUTED, strokeWidth: 1 }} />
        {replayPct !== undefined && (
          <ReferenceLine
            x={replayPct}
            stroke={MUTED}
            strokeDasharray="4 3"
            label={{ value: replayLabel, position: 'top', fill: '#f2efe9', fontSize: 11 }}
          />
        )}
        {skipPct !== undefined && (
          <ReferenceLine
            x={skipPct}
            stroke={MUTED}
            strokeDasharray="4 3"
            label={{ value: skipLabel, position: 'insideBottom', fill: '#f2efe9', fontSize: 11 }}
          />
        )}
        <Line isAnimationActive={false} type="monotone" dataKey="audience" stroke={SERIES_1} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function Dashboard({ t }: { t: Strings }) {
  const [m, setM] = useState<Metrics | null>(null)
  const [tab, setTab] = useState<Tab>(() => {
    const sub = window.location.hash.split('/')[1]
    return sub === 'topics' || sub === 'episodes' ? sub : 'general'
  })
  const [episodes, setEpisodes] = useState<EpisodeStats[] | null>(null)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [analyzing, setAnalyzing] = useState(false)

  const analyze = async () => {
    if (!selectedId) return
    setAnalyzing(true)
    setAnalysis(null)
    try {
      const r = await fetch(`/api/metrics/episodes/${selectedId}/analyze`, { method: 'POST' })
      if (r.ok) setAnalysis(await r.json())
    } finally {
      setAnalyzing(false)
    }
  }

  useEffect(() => {
    fetch('/api/metrics')
      .then((r) => r.json())
      .then(setM)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (tab !== 'episodes' || episodes) return
    fetch('/api/metrics/episodes')
      .then((r) => r.json())
      .then((data: EpisodeStats[]) => {
        setEpisodes(data)
        if (data.length) setSelectedId(data[0].story_id)
      })
      .catch(() => {})
  }, [tab, episodes])

  if (!m) return <p className="px-8 pt-28 text-white/40 md:px-14">{t.loading}</p>

  const k = m.kpis as Record<string, number> & { peak_hour: string }
  const series = m.series.map((d) => ({
    ...d,
    label: shortDate(d.date),
    cost_per_listener: +(((d.llm_cost + d.tts_cost) * 30) / d.users).toFixed(3),
  }))
  const peakPlays = Math.max(...m.hourly.map((h) => h.plays))
  const episode = episodes?.find((e) => e.story_id === selectedId) ?? null

  const tabs: { key: Tab; label: string }[] = [
    { key: 'general', label: t.dashTabGeneral },
    { key: 'topics', label: t.dashTabTopics },
    { key: 'episodes', label: t.dashTabEpisodes },
  ]

  return (
    <div className="px-8 pt-24 pb-16 md:px-14">
      <h1 className="font-display text-3xl font-800 text-white">{t.dashTitle}</h1>
      <p className="mt-1 text-sm text-white/45">{t.dashSubtitle}</p>

      <div className="mt-5 flex gap-2">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`cursor-pointer rounded-full px-4 py-1.5 text-sm transition ${
              tab === key
                ? 'bg-ember font-semibold text-white'
                : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'general' && (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
            <Tile label={t.dashMau} value={k.mau.toLocaleString()} />
            <Tile label={t.dashPaid} value={k.paid_users.toLocaleString()} hint={`${(k.paid_pct * 100).toFixed(1)}% conv.`} />
            <Tile label={t.dashPlaysDay} value={k.plays_day.toLocaleString()} />
            <Tile label={t.dashListenersDay} value={k.listeners_day.toLocaleString()} />
            <Tile label={t.dashEngaged} value={`${Math.round(k.engaged_pct * 100)}%`} />
            <Tile label={t.dashCompletion} value={`${Math.round(k.completion * 100)}%`} />
            <Tile label={t.dashCostGeneration} value={`${k.cost_per_generation.toFixed(2)} €`} />
            <Tile label={t.dashCostUserDay} value={`${k.cost_per_user_day.toFixed(3)} €`} />
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4">
            <Tile label={t.dashPeakHour} value={String(k.peak_hour)} />
            <Tile label={t.dashMinListen} value={`${k.avg_minutes_per_listen}`} />
            <Tile label={t.dashMargin} value={`${Math.round(k.gross_margin * 100)}%`} />
            <Tile label={t.dashSavingsReuse} value={`${k.savings_reuse.toLocaleString()} €`} />
          </div>

          <p className="mt-4 max-w-3xl text-xs leading-relaxed text-white/40">{t.dashMockNote}</p>

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <Panel title={t.dashDau}>
              <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                <AreaChart data={series} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
                  <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                  <XAxis dataKey="label" {...axisProps} minTickGap={28} />
                  <YAxis {...axisProps} />
                  <Tooltip {...tooltipStyle} cursor={{ stroke: MUTED, strokeWidth: 1 }} />
                  <Area isAnimationActive={false} type="monotone" dataKey="dau" stroke={SERIES_1} strokeWidth={2} fill={SERIES_1} fillOpacity={0.15} />
                </AreaChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title={t.dashHourly}>
              <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                <BarChart data={m.hourly} margin={{ top: 14, right: 8, bottom: 0, left: -12 }}>
                  <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                  <XAxis dataKey="hour" {...axisProps} minTickGap={16} />
                  <YAxis {...axisProps} />
                  <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Bar isAnimationActive={false} dataKey="plays" fill={SERIES_1} radius={[3, 3, 0, 0]}>
                    <LabelList
                      dataKey="plays"
                      position="top"
                      content={(props) => {
                        const { x, y, width, value } = props as { x: number; y: number; width: number; value: number }
                        if (value !== peakPlays) return null
                        return (
                          <text x={x + width / 2} y={y - 5} textAnchor="middle" fill="#f2efe9" fontSize={11} fontWeight={600}>
                            {value}
                          </text>
                        )
                      }}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title={t.dashGenVsReuse}>
              <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                <BarChart data={series} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
                  <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                  <XAxis dataKey="label" {...axisProps} minTickGap={28} />
                  <YAxis {...axisProps} />
                  <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Legend wrapperStyle={{ fontSize: 12, color: MUTED }} />
                  <Bar isAnimationActive={false} dataKey="generated" name={t.dashGenerated} stackId="g" fill={SERIES_1} stroke={SURFACE} strokeWidth={1} />
                  <Bar isAnimationActive={false} dataKey="reused" name={t.dashReused} stackId="g" fill={SERIES_2} stroke={SURFACE} strokeWidth={1} radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title={t.dashRetentionGeneral}>
              <RetentionChart data={m.retention} />
            </Panel>

            <Panel title={t.dashDailyCost}>
              <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                <BarChart data={series} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
                  <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                  <XAxis dataKey="label" {...axisProps} minTickGap={28} />
                  <YAxis {...axisProps} />
                  <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Legend wrapperStyle={{ fontSize: 12, color: MUTED }} />
                  <Bar isAnimationActive={false} dataKey="llm_cost" name={t.dashLlm} stackId="c" fill={SERIES_1} stroke={SURFACE} strokeWidth={1} />
                  <Bar isAnimationActive={false} dataKey="tts_cost" name={t.dashTts} stackId="c" fill={SERIES_2} stroke={SURFACE} strokeWidth={1} radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title={t.dashCostPerListener}>
              <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                <LineChart data={series} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
                  <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                  <XAxis dataKey="label" {...axisProps} minTickGap={28} />
                  <YAxis {...axisProps} tickFormatter={(v: number) => `${v}€`} />
                  <Tooltip {...tooltipStyle} cursor={{ stroke: MUTED, strokeWidth: 1 }} />
                  <Line isAnimationActive={false} type="monotone" dataKey="cost_per_listener" stroke={SERIES_1} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </Panel>
          </div>

          <div className="mt-4 rounded-xl bg-ink-soft p-4">
            <p className="mb-3 text-[11px] font-semibold tracking-wide text-white/50 uppercase">
              {t.dashCohorts}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-center text-xs" style={{ fontVariantNumeric: 'tabular-nums' }}>
                <thead>
                  <tr className="text-[10px] tracking-wide text-white/40 uppercase">
                    <th className="pb-2 pr-2 text-left font-medium">Cohorte</th>
                    <th className="pb-2 pr-2 text-right font-medium">{t.dashCohortUsers}</th>
                    {Array.from({ length: 9 }).map((_, i) => (
                      <th key={i} className="pb-2 font-medium">
                        {t.dashWeekAbbr}
                        {i}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {m.cohorts.map((c) => (
                    <tr key={c.cohort}>
                      <td className="py-0.5 pr-2 text-left text-white/60">{shortDate(c.cohort)}</td>
                      <td className="py-0.5 pr-2 text-right text-white/60">{c.size}</td>
                      {Array.from({ length: 9 }).map((_, i) => {
                        const value = c.weeks[i]
                        if (value === undefined) return <td key={i} />
                        return (
                          <td key={i} className="p-0.5">
                            <div
                              className="rounded px-1 py-1.5 text-white/85"
                              style={{ background: `rgba(57, 135, 229, ${0.06 + (value / 100) * 0.8})` }}
                            >
                              {Math.round(value)}%
                            </div>
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-emerald-500/20 bg-ink-soft p-4">
            <p className="text-[11px] font-semibold tracking-wide text-emerald-400 uppercase">{t.dashReal}</p>
            <p className="mt-0.5 text-xs text-white/40">{t.dashRealHint}</p>
            <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4">
              <Tile label={t.dashRealEpisodes} value={String(m.real.episodes)} />
              <Tile label={t.dashRealAvgMin} value={`${m.real.avg_episode_minutes} ${t.min}`} />
            </div>
            <table className="mt-4 w-full text-left text-sm" style={{ fontVariantNumeric: 'tabular-nums' }}>
              <thead>
                <tr className="text-[11px] tracking-wide text-white/40 uppercase">
                  <th className="pb-2 font-medium">Tipo</th>
                  <th className="pb-2 font-medium">{t.dashCalls}</th>
                  <th className="pb-2 font-medium">{t.dashTokens}</th>
                  <th className="pb-2 font-medium">{t.dashChars}</th>
                  <th className="pb-2 font-medium">USD</th>
                </tr>
              </thead>
              <tbody className="text-cream/80">
                {m.real.by_kind.map((row) => (
                  <tr key={row.kind} className="border-t border-white/5">
                    <td className="py-1.5">{row.kind}</td>
                    <td className="py-1.5">{row.calls}</td>
                    <td className="py-1.5">{row.tokens.toLocaleString()}</td>
                    <td className="py-1.5">{row.characters.toLocaleString()}</td>
                    <td className="py-1.5">{row.cost_usd.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'topics' && (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <Panel title={t.dashListensByCat}>
            <ResponsiveContainer width="100%" height={220} initialDimension={CHART_DIM}>
              <BarChart data={m.per_category} layout="vertical" margin={{ top: 0, right: 24, bottom: 0, left: 8 }}>
                <CartesianGrid stroke={GRID} strokeWidth={1} horizontal={false} />
                <XAxis type="number" {...axisProps} />
                <YAxis type="category" dataKey="category" {...axisProps} width={70} />
                <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                <Bar isAnimationActive={false} dataKey="listens" fill={SERIES_1} barSize={14} radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title={t.dashCostByCat}>
            <ResponsiveContainer width="100%" height={220} initialDimension={CHART_DIM}>
              <BarChart data={m.per_category} layout="vertical" margin={{ top: 0, right: 24, bottom: 0, left: 8 }}>
                <CartesianGrid stroke={GRID} strokeWidth={1} horizontal={false} />
                <XAxis type="number" {...axisProps} tickFormatter={(v: number) => `${v}€`} />
                <YAxis type="category" dataKey="category" {...axisProps} width={70} />
                <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                <Bar isAnimationActive={false} dataKey="cost_per_episode" fill={SERIES_1} barSize={14} radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title={t.dashTopEpisodes} span>
            <table className="w-full text-left text-sm" style={{ fontVariantNumeric: 'tabular-nums' }}>
              <thead>
                <tr className="text-[11px] tracking-wide text-white/40 uppercase">
                  <th className="pb-2 font-medium">Ep.</th>
                  <th className="pb-2 text-right font-medium">{t.dashPlaysCol}</th>
                  <th className="pb-2 text-right font-medium">{t.dashCompletionCol}</th>
                </tr>
              </thead>
              <tbody className="text-cream/80">
                {m.top_episodes.map((e) => (
                  <tr key={e.title} className="border-t border-white/5">
                    <td className="max-w-0 truncate py-2 pr-3" title={e.title}>
                      {e.title}
                      <span className="ml-1.5 text-[11px] text-white/35">{e.category}</span>
                    </td>
                    <td className="py-2 text-right">{e.plays.toLocaleString()}</td>
                    <td className="py-2 text-right">{Math.round(e.completion * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </div>
      )}

      {tab === 'episodes' && (
        <div className="mt-6">
          <label className="mb-2 block text-[11px] font-semibold tracking-wide text-white/50 uppercase">
            {t.dashEpisodeSelect}
          </label>
          <select
            value={selectedId ?? ''}
            onChange={(e) => {
              setSelectedId(Number(e.target.value))
              setAnalysis(null)
            }}
            className="w-full max-w-xl cursor-pointer rounded-lg border border-white/10 bg-ink-soft p-3 text-sm text-cream focus:border-ember/60 focus:outline-none"
          >
            {(episodes ?? []).map((e) => (
              <option key={e.story_id} value={e.story_id}>
                #{e.story_id} · [{e.category}] {e.title}
              </option>
            ))}
          </select>

          {!episodes && <p className="mt-6 text-white/40">{t.loading}</p>}

          {episode && (
            <>
              <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-3">
                <Tile label={t.dashPlaysCol} value={episode.plays.toLocaleString()} />
                <Tile label={t.dashListeners} value={episode.listeners.toLocaleString()} />
                <Tile label={t.dashCompletionCol} value={`${Math.round(episode.completion * 100)}%`} />
                <Tile
                  label={t.dashDuration}
                  value={episode.duration_s ? `${(episode.duration_s / 60).toFixed(1)} ${t.min}` : '—'}
                />
                <Tile label={t.dashReplay} value={`${episode.most_replayed_pct}%`} />
                <Tile label={t.dashSkipped} value={`${episode.most_skipped_pct}%`} />
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <Panel title={t.dashRetention}>
                  <RetentionChart
                    data={episode.retention}
                    replayPct={episode.most_replayed_pct}
                    skipPct={episode.most_skipped_pct}
                    replayLabel={t.markReplay}
                    skipLabel={t.markSkip}
                  />
                </Panel>
                <Panel title={t.dashDaySince}>
                  <ResponsiveContainer width="100%" height={200} initialDimension={CHART_DIM}>
                    <BarChart data={episode.daily} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
                      <CartesianGrid stroke={GRID} strokeWidth={1} vertical={false} />
                      <XAxis dataKey="day" {...axisProps} />
                      <YAxis {...axisProps} />
                      <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                      <Bar isAnimationActive={false} dataKey="plays" fill={SERIES_1} radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Panel>
              </div>

              <button
                onClick={analyze}
                disabled={analyzing}
                className="mt-4 cursor-pointer rounded-lg bg-ember px-5 py-2.5 font-display text-sm font-700 text-white shadow-lg shadow-ember/25 transition hover:brightness-110 disabled:cursor-wait disabled:opacity-60"
              >
                {analyzing ? t.dashAnalyzing : t.dashAnalyze}
              </button>

              {analysis && (
                <div className="mt-4 rounded-xl border border-ember/25 bg-ink-soft p-5">
                  <p className="text-[11px] font-semibold tracking-wide text-ember uppercase">
                    {t.dashAnalysis}
                  </p>
                  <ul className="mt-3 space-y-2 text-sm leading-relaxed text-cream/85">
                    {analysis.insights.map((insight, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-ember">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                  {analysis.recommendation && (
                    <p className="mt-4 text-sm text-cream/90">
                      <span className="font-display font-700 text-white">
                        {t.dashRecommendation}:{' '}
                      </span>
                      {analysis.recommendation}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
