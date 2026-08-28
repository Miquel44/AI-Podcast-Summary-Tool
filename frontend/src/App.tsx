import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { CategoryRow } from './components/CategoryRow'
import { Hero } from './components/Hero'
import { StoryCard } from './components/StoryCard'
import { InterestsModal } from './components/InterestsModal'
import { PlayerBar, type NowPlaying } from './components/PlayerBar'
import { StoryModal } from './components/StoryModal'
import { LANGS, STRINGS, type Lang } from './i18n'
import type { Category, Episode, Story, StoryDetail } from './types'

// The dashboard pulls the whole charting library — load it only when opened.
// If the lazy chunk 404s (stale tab open across a redeploy), reload once to
// pick up the fresh build instead of hanging on the loading state.
const Dashboard = lazy(() =>
  import('./components/Dashboard')
    .then((m) => ({ default: m.Dashboard }))
    .catch(() => {
      window.location.reload()
      return new Promise<never>(() => {})
    }),
)

export default function App() {
  const [categories, setCategories] = useState<Category[]>([])
  const [storiesByCat, setStoriesByCat] = useState<Record<number, Story[]>>({})
  const [selected, setSelected] = useState<Story | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lang, setLang] = useState<Lang>('es')
  const [view, setView] = useState<'home' | 'dashboard' | 'demo'>(
    window.location.hash.startsWith('#dashboard') ? 'dashboard' : 'home',
  )
  const [demoStories, setDemoStories] = useState<Story[] | null>(null)

  useEffect(() => {
    if (view !== 'demo' || demoStories) return
    fetch('/api/demo')
      .then((r) => r.json())
      .then(setDemoStories)
      .catch(() => setDemoStories([]))
  }, [view, demoStories])
  const [showInterests, setShowInterests] = useState(false)
  const [query, setQuery] = useState('')
  const [heroIdx, setHeroIdx] = useState(0)
  const [nowPlaying, setNowPlaying] = useState<NowPlaying | null>(null)

  const handlePlay = (story: StoryDetail, episode: Episode) => {
    setNowPlaying({ story, episode })
  }

  const t = STRINGS[lang]

  const loadStories = useCallback(async (cats: Category[]) => {
    const entries = await Promise.all(
      cats.map(async (c) => [c.id, await api.stories(c.id).catch(() => [])] as const),
    )
    setStoriesByCat(Object.fromEntries(entries))
  }, [])

  const loadAll = useCallback(async () => {
    const cats = (await api.categories()).filter((c) => c.enabled)
    setCategories(cats)
    await loadStories(cats)
  }, [loadStories])

  useEffect(() => {
    api.settings().then((s) => {
      if (LANGS.includes(s.language as Lang)) setLang(s.language as Lang)
    })
    loadAll().catch((e) => setError(String(e)))
  }, [loadAll])

  // The backend prepares the daily edition on its own; poll quietly so rows
  // fill in and card statuses update without any user action. Re-fetches the
  // category list too, so newly added interests appear without a reload.
  // Paused while the tab is hidden to avoid useless requests.
  useEffect(() => {
    if (!categories.length) return
    const timer = setInterval(() => {
      if (!document.hidden) loadAll().catch(() => {})
    }, 6000)
    return () => clearInterval(timer)
  }, [categories, loadAll])

  const changeLanguage = async (next: Lang) => {
    if (next === lang) return
    if (!window.confirm(t.langWarning)) return
    try {
      await fetch('/api/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: next }),
      })
      setLang(next)
      setSelected(null)
      await loadAll()
    } catch (e) {
      setError(String(e))
    }
  }

  const handleDiscover = async (category: Category) => {
    try {
      await api.discover(category.id)
      const stories = await api.stories(category.id)
      setStoriesByCat((prev) => ({ ...prev, [category.id]: stories }))
    } catch (e) {
      setError(`${category.title}: ${String(e)}`)
    }
  }

  const allStories = Object.values(storiesByCat).flat()

  // Netflix-style rotating hero: one candidate per category (ready > image).
  const featuredList = useMemo(() => {
    return categories
      .map((c) => {
        const stories = storiesByCat[c.id] ?? []
        return (
          stories.find((s) => s.status === 'ready') ??
          stories.find((s) => s.cover_image) ??
          stories[0]
        )
      })
      .filter((s): s is Story => Boolean(s))
  }, [categories, storiesByCat])

  useEffect(() => {
    if (featuredList.length < 2) return
    const timer = setInterval(() => {
      if (!document.hidden) setHeroIdx((i) => (i + 1) % featuredList.length)
    }, 7000)
    return () => clearInterval(timer)
  }, [featuredList.length])

  const featured = featuredList[heroIdx % Math.max(featuredList.length, 1)]

  const trimmed = query.trim().toLowerCase()
  const searchResults = trimmed
    ? allStories.filter((s) =>
        `${s.title} ${s.tagline} ${s.summary}`.toLowerCase().includes(trimmed),
      )
    : []

  return (
    <div className="min-h-screen bg-ink font-body text-cream">
      <nav className="absolute top-0 right-0 left-0 z-20 flex items-center justify-between px-8 py-6 md:px-14">
        <button
          onClick={() => setView('home')}
          className="cursor-pointer font-display text-xl font-800 tracking-[0.35em] text-white"
        >
          ONDA
        </button>
        <div className="flex items-center gap-5 text-sm text-white/60">
          {view === 'home' && (
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t.searchPlaceholder}
              className="w-40 rounded-full border border-white/10 bg-black/30 px-3.5 py-1.5 text-sm text-cream backdrop-blur-sm transition placeholder:text-white/30 focus:w-56 focus:border-ember/50 focus:outline-none md:w-48"
            />
          )}
          <button
            onClick={() => setView('demo')}
            className={`cursor-pointer transition hover:text-white ${view === 'demo' ? 'font-semibold text-white' : ''}`}
          >
            {t.navDemo}
          </button>
          <button
            onClick={() => setShowInterests(true)}
            className="cursor-pointer transition hover:text-white"
          >
            {t.interests}
          </button>
          <button
            onClick={() => setView(view === 'dashboard' ? 'home' : 'dashboard')}
            className="cursor-pointer transition hover:text-white"
          >
            {view === 'dashboard' ? t.home : t.dashboard}
          </button>
          <span className="flex items-center gap-1.5 rounded-full bg-white/5 px-2.5 py-1 text-xs">
            {LANGS.map((l) => (
              <button
                key={l}
                onClick={() => changeLanguage(l)}
                className={`cursor-pointer rounded-full px-1.5 py-0.5 uppercase transition ${
                  l === lang ? 'bg-ember font-bold text-white' : 'text-white/50 hover:text-white'
                }`}
              >
                {l}
              </button>
            ))}
          </span>
        </div>
      </nav>

      {error && (
        <div className="fixed right-4 bottom-4 z-50 max-w-sm rounded-lg bg-red-950/90 p-3 text-xs text-red-200 shadow-xl">
          {error}
          <button onClick={() => setError(null)} className="ml-2 cursor-pointer font-bold">
            ✕
          </button>
        </div>
      )}

      {view === 'dashboard' ? (
        <Suspense
          fallback={<p className="px-8 pt-28 text-white/40 md:px-14">{t.loading}</p>}
        >
          <Dashboard t={t} />
        </Suspense>
      ) : view === 'demo' ? (
        <main className="px-8 pt-24 pb-20 md:px-14">
          <h1 className="font-display text-3xl font-800 text-white">{t.navDemo}</h1>
          <p className="mt-2 max-w-xl text-sm text-white/50">{t.demoNote}</p>
          <div className="mt-6 flex flex-wrap gap-4">
            {(demoStories ?? []).map((story) => (
              <StoryCard key={story.id} story={story} onClick={() => setSelected(story)} t={t} />
            ))}
          </div>
          {demoStories === null && <p className="mt-6 text-white/40">{t.loading}</p>}
        </main>
      ) : trimmed ? (
        <main className="px-8 pt-24 pb-20 md:px-14">
          <p className="mb-5 text-sm text-white/50">
            {searchResults.length === 0 && `${t.searchEmpty} «${query.trim()}»`}
          </p>
          <div className="flex flex-wrap gap-4">
            {searchResults.map((story) => (
              <StoryCard key={story.id} story={story} onClick={() => setSelected(story)} t={t} />
            ))}
          </div>
        </main>
      ) : (
        <>
          {featured ? (
            <Hero
              story={featured}
              onSelect={setSelected}
              t={t}
              count={featuredList.length}
              index={heroIdx % Math.max(featuredList.length, 1)}
              onDot={setHeroIdx}
            />
          ) : (
            <div className="px-8 pt-28 pb-4 md:px-14">
              <h1 className="max-w-2xl font-display text-4xl leading-tight font-800 text-white">
                {t.emptyTitle}
              </h1>
              <p className="mt-3 max-w-lg text-white/60">{t.emptySub}</p>
            </div>
          )}

          <main className="pb-20">
            {categories.map((cat) => (
              <CategoryRow
                key={cat.id}
                category={cat}
                stories={storiesByCat[cat.id] ?? []}
                onDiscover={handleDiscover}
                onSelect={setSelected}
                t={t}
              />
            ))}
          </main>
        </>
      )}

      {nowPlaying && <div className="h-14" />}

      {selected && (
        <StoryModal
          storyId={selected.id}
          category={categories.find((c) => c.id === selected.category_id)}
          onClose={() => setSelected(null)}
          onChanged={() => loadStories(categories)}
          onPlay={handlePlay}
          t={t}
        />
      )}
      {nowPlaying && (
        <PlayerBar
          nowPlaying={nowPlaying}
          onClose={() => setNowPlaying(null)}
          onOpenStory={(story) => setSelected(story)}
        />
      )}
      {showInterests && (
        <InterestsModal
          t={t}
          onClose={() => setShowInterests(false)}
          onApplied={() => loadAll()}
        />
      )}
    </div>
  )
}
