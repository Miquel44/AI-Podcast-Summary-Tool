import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Strings } from '../i18n'
import type { Category, StoryDetail } from '../types'

export function StoryModal({
  storyId,
  category,
  onClose,
  onChanged,
  onPlay,
  t,
}: {
  storyId: number
  category: Category | undefined
  onClose: () => void
  onChanged: () => void
  onPlay: (story: StoryDetail, episode: StoryDetail['episodes'][number]) => void
  t: Strings
}) {
  const [story, setStory] = useState<StoryDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = () => api.story(storyId).then(setStory).catch((e) => setError(String(e)))

  useEffect(() => {
    refresh()
  }, [storyId])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  // Poll while generating so the player appears without reloading.
  useEffect(() => {
    if (story?.status !== 'generating') return
    const t = setInterval(() => {
      refresh()
      onChanged()
    }, 4000)
    return () => clearInterval(t)
  }, [story?.status])

  const generate = async () => {
    setError(null)
    try {
      setStory(await api.generate(storyId))
      onChanged()
    } catch (e) {
      setError(String(e))
    }
  }

  const episode = story?.episodes.find((e) => e.audio_path) ?? story?.episodes[0]
  const hostsLabel =
    category && category.hosts.length >= 2
      ? `${t.dialogue}: ${category.hosts.map((h) => h.voice_name).join(' · ')}`
      : t.oneVoice

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm md:items-center"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-t-2xl bg-ink-soft shadow-2xl md:rounded-2xl"
      >
        {story && (
          <>
            <div
              className="relative flex h-44 items-end overflow-hidden rounded-t-2xl p-6"
              style={{
                background: `linear-gradient(140deg, ${story.cover_from} 0%, ${story.cover_to} 100%)`,
              }}
            >
              {story.cover_image ? (
                <img
                  src={story.cover_image}
                  alt=""
                  className="absolute inset-0 h-full w-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
              ) : (
                <span aria-hidden className="absolute -right-4 -top-6 text-[8rem] opacity-40">
                  {story.icon}
                </span>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
              <div className="relative">
                <h2 className="font-display text-3xl leading-tight font-800 text-white">
                  {story.title}
                </h2>
                <p className="mt-1 text-sm text-white/70">{story.tagline}</p>
                {story.source_articles.length > 0 && (
                  <p className="mt-1.5 text-[11px] font-medium tracking-wide text-white/55">
                    {[...new Set(story.source_articles.map((a) => a.source))].join(' · ')}
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                aria-label={t.close}
                className="absolute top-4 right-4 flex h-9 w-9 cursor-pointer items-center justify-center rounded-full bg-black/40 text-white/80 backdrop-blur-sm transition hover:bg-black/70"
              >
                ✕
              </button>
            </div>

            <div className="space-y-5 p-6">
              <p className="text-[15px] leading-relaxed text-cream/85">{story.summary}</p>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs tracking-wide text-white/40 uppercase">{hostsLabel}</p>
                {story.cover_credit && (
                  <p className="text-[10px] text-white/25">{story.cover_credit}</p>
                )}
              </div>

              {story.status !== 'ready' && (
                <button
                  onClick={generate}
                  disabled={story.status === 'generating'}
                  className="w-full cursor-pointer rounded-lg bg-ember py-3.5 font-display text-sm font-700 text-white shadow-lg shadow-ember/25 transition hover:brightness-110 disabled:cursor-wait disabled:bg-amber-500 disabled:shadow-none"
                >
                  {story.status === 'generating'
                    ? t.modalGenerating
                    : story.status === 'failed'
                      ? t.modalRetry
                      : t.generate}
                </button>
              )}

              {episode?.audio_path && (
                <div className="flex items-center justify-between gap-4 rounded-xl bg-black/30 p-4">
                  <p className="min-w-0 font-display text-sm font-600 text-white">
                    <span className="block truncate">{episode.title}</span>
                    {episode.duration_s && (
                      <span className="text-white/40">
                        {Math.round(episode.duration_s / 60)} {t.min}
                      </span>
                    )}
                  </p>
                  <button
                    onClick={() => onPlay(story, episode)}
                    className="shrink-0 cursor-pointer rounded-full bg-white px-5 py-2.5 font-display text-sm font-700 text-ink transition hover:scale-105"
                  >
                    {t.playNow}
                  </button>
                </div>
              )}

              {story.status === 'ready' && (
                <button
                  onClick={generate}
                  className="w-full cursor-pointer rounded-lg border border-white/15 bg-white/5 py-2.5 text-sm font-medium text-white/70 transition hover:bg-white/10 hover:text-white"
                >
                  {t.modalRegenerate}
                </button>
              )}

              {story.status === 'failed' && episode?.error && (
                <p className="rounded-lg bg-red-950/60 p-3 text-xs text-red-300">{episode.error}</p>
              )}
              {error && <p className="rounded-lg bg-red-950/60 p-3 text-xs text-red-300">{error}</p>}

              {episode?.script && episode.script.length > 0 && (
                <details className="rounded-xl bg-black/20 p-4">
                  <summary className="cursor-pointer font-display text-sm font-600 text-white/70">
                    {t.scriptLabel}
                  </summary>
                  <div className="mt-3 space-y-2 text-sm leading-relaxed text-cream/75">
                    {episode.script.map((line, i) => (
                      <p key={i}>
                        {category && category.hosts.length >= 2 && (
                          <span className="font-600 text-ember">
                            {category.hosts[line.host]?.voice_name ?? `Voz ${line.host}`}:{' '}
                          </span>
                        )}
                        {line.text}
                      </p>
                    ))}
                  </div>
                </details>
              )}

              {story.source_articles.length > 0 && (
                <div>
                  <p className="mb-2 font-display text-xs font-600 tracking-[0.15em] text-white/40 uppercase">
                    {t.sources}
                  </p>
                  <ul className="space-y-1.5">
                    {story.source_articles.map((a, i) => (
                      <li key={i} className="text-sm">
                        <a
                          href={a.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cream/70 underline decoration-white/20 underline-offset-2 transition hover:text-ember"
                        >
                          <span className="text-white/40">[{a.source}]</span> {a.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </>
        )}
        {!story && !error && <p className="p-10 text-center text-white/40">{t.loading}</p>}
        {!story && error && <p className="p-10 text-center text-sm text-red-300">{error}</p>}
      </div>
    </div>
  )
}
