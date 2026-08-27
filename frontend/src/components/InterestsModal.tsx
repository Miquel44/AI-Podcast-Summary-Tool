import { useEffect, useRef, useState } from 'react'
import type { Strings } from '../i18n'

interface Suggestions {
  recommended: { slug: string; title: string; enabled: boolean }[]
  extra: string[]
}

export function InterestsModal({
  t,
  onClose,
  onApplied,
}: {
  t: Strings
  onClose: () => void
  onApplied: () => void
}) {
  const [sug, setSug] = useState<Suggestions | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [custom, setCustom] = useState<string[]>([])
  const [text, setText] = useState('')
  const [busy, setBusy] = useState<'analyze' | 'apply' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('/api/interests/suggestions')
      .then((r) => r.json())
      .then((s: Suggestions) => {
        setSug(s)
        setSelected(new Set(s.recommended.filter((r) => r.enabled).map((r) => r.title)))
      })
      .catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const toggle = (topic: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(topic)) next.delete(topic)
      else next.add(topic)
      return next
    })
  }

  const addTags = (tags: string[]) => {
    // A tag matching an existing chip selects that chip (canonical name)
    // instead of duplicating it as a custom one.
    const canonical = tags.map((tag) => {
      const rec = sug?.recommended.find((r) => r.title.toLowerCase() === tag.toLowerCase())
      if (rec) return rec.title
      return sug?.extra.find((x) => x.toLowerCase() === tag.toLowerCase()) ?? tag
    })
    const known = new Set(
      [...(sug?.recommended.map((r) => r.title) ?? []), ...(sug?.extra ?? [])].map((x) =>
        x.toLowerCase(),
      ),
    )
    setCustom((prev) => [
      ...prev,
      ...canonical.filter(
        (tag) =>
          !known.has(tag.toLowerCase()) &&
          !prev.some((p) => p.toLowerCase() === tag.toLowerCase()),
      ),
    ])
    setSelected((prev) => new Set([...prev, ...canonical]))
  }

  const analyzeText = async () => {
    setBusy('analyze')
    setError(null)
    try {
      const r = await fetch('/api/interests/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      if (!r.ok) throw new Error(await r.text())
      addTags((await r.json()).tags)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(null)
    }
  }

  const analyzeAudio = async (file: File) => {
    setBusy('analyze')
    setError(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const r = await fetch('/api/interests/analyze-audio', { method: 'POST', body: form })
      if (!r.ok) throw new Error(await r.text())
      addTags((await r.json()).tags)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(null)
    }
  }

  const apply = async () => {
    if (!sug) return
    const recommendedEnabled = new Set(
      sug.recommended.filter((r) => r.enabled).map((r) => r.title),
    )
    const hasNew = [...selected].some((topic) => !recommendedEnabled.has(topic))
    if (hasNew && !window.confirm(t.intCostWarning)) return
    setBusy('apply')
    setError(null)
    try {
      const r = await fetch('/api/interests/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topics: [...selected] }),
      })
      if (!r.ok) throw new Error(await r.text())
      onApplied()
      onClose()
    } catch (e) {
      setError(String(e))
      setBusy(null)
    }
  }

  const chip = (topic: string, recommended = false) => (
    <button
      key={topic}
      onClick={() => toggle(topic)}
      className={`cursor-pointer rounded-full px-3.5 py-1.5 text-sm transition ${
        selected.has(topic)
          ? 'bg-ember font-semibold text-white'
          : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
      }`}
    >
      {recommended && '✦ '}
      {topic}
    </button>
  )

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm md:items-center"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-t-2xl bg-ink-soft p-6 shadow-2xl md:rounded-2xl"
      >
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-display text-2xl font-800 text-white">{t.intTitle}</h2>
            <p className="mt-1 max-w-md text-sm text-white/50">{t.intSubtitle}</p>
          </div>
          <button
            onClick={onClose}
            aria-label={t.close}
            className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full bg-black/40 text-white/80 transition hover:bg-black/70"
          >
            ✕
          </button>
        </div>

        {sug && (
          <>
            <p className="mt-5 font-display text-xs font-600 tracking-[0.15em] text-white/40 uppercase">
              {t.intRecommended} <span className="normal-case tracking-normal">· {t.intRecommendedHint}</span>
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {sug.recommended.map((r) => chip(r.title, true))}
            </div>

            <p className="mt-5 font-display text-xs font-600 tracking-[0.15em] text-white/40 uppercase">
              {t.intExtra}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {sug.extra.map((topic) => chip(topic))}
              {custom.map((topic) => chip(topic))}
            </div>

            <p className="mt-5 font-display text-xs font-600 tracking-[0.15em] text-white/40 uppercase">
              {t.intDescribe}
            </p>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t.intPlaceholder}
              rows={2}
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/25 p-3 text-sm text-cream placeholder:text-white/25 focus:border-ember/60 focus:outline-none"
            />
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={analyzeText}
                disabled={busy !== null || !text.trim()}
                className="cursor-pointer rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {busy === 'analyze' ? t.intAnalyzing : t.intAnalyze}
              </button>
              <button
                onClick={() => fileRef.current?.click()}
                disabled={busy !== null}
                className="cursor-pointer rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20 disabled:opacity-40"
              >
                🎤 {t.intAudio}
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && analyzeAudio(e.target.files[0])}
              />
            </div>

            {error && (
              <p className="mt-3 rounded-lg bg-red-950/60 p-3 text-xs text-red-300">{error}</p>
            )}

            <button
              onClick={apply}
              disabled={busy !== null || selected.size === 0}
              className="mt-6 w-full cursor-pointer rounded-lg bg-ember py-3.5 font-display text-sm font-700 text-white shadow-lg shadow-ember/25 transition hover:brightness-110 disabled:cursor-wait disabled:opacity-50"
            >
              {busy === 'apply' ? t.intApplying : t.intApply}
            </button>
          </>
        )}
        {!sug && !error && <p className="mt-8 text-center text-white/40">{t.loading}</p>}
      </div>
    </div>
  )
}
