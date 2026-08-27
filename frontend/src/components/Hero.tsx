import type { Show } from '../types'

export function Hero({ show, onSelect }: { show: Show; onSelect: (show: Show) => void }) {
  const hostsLabel =
    show.hosts.length >= 2
      ? `Diálogo a ${show.hosts.length} voces · ${show.hosts.map((h) => h.voice_name).join(' y ')}`
      : 'Narrado a una voz'

  return (
    <header className="relative overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(120deg, ${show.cover_from}cc 0%, ${show.cover_to}55 45%, transparent 75%), radial-gradient(90% 120% at 85% 0%, ${show.cover_to}33 0%, transparent 60%)`,
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/40 to-transparent" />

      <div className="relative px-8 pt-24 pb-16 md:px-14 md:pt-32">
        <p className="font-display text-xs font-600 tracking-[0.3em] text-white/60 uppercase">
          Episodio destacado
        </p>
        <h1 className="mt-3 max-w-xl font-display text-5xl leading-[1.05] font-800 text-white md:text-6xl">
          {show.title}
        </h1>
        <p className="mt-4 max-w-lg text-base text-white/75">{show.tagline}</p>
        <p className="mt-2 text-sm text-white/50">{hostsLabel}</p>
        <div className="mt-8 flex items-center gap-3">
          <button
            onClick={() => onSelect(show)}
            className="cursor-pointer rounded-lg bg-cream px-6 py-3 font-display text-sm font-700 text-ink transition hover:bg-white"
          >
            ▶ Generar episodio
          </button>
          <button
            onClick={() => onSelect(show)}
            className="cursor-pointer rounded-lg border border-white/25 bg-white/5 px-6 py-3 font-display text-sm font-600 text-white backdrop-blur-sm transition hover:bg-white/15"
          >
            Elegir voces
          </button>
        </div>
      </div>
    </header>
  )
}
