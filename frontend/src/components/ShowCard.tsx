import type { Show } from '../types'

export function ShowCard({ show, onClick }: { show: Show; onClick?: () => void }) {
  const voiceLabel =
    show.hosts.length === 0
      ? 'Voz por defecto'
      : show.hosts.length === 1
        ? show.hosts[0].voice_name
        : `${show.hosts.length} voces`

  return (
    <button
      onClick={onClick}
      className="group relative w-44 shrink-0 cursor-pointer overflow-hidden rounded-xl text-left transition-transform duration-300 ease-out hover:z-10 hover:scale-105 focus-visible:scale-105 focus-visible:outline-2 focus-visible:outline-ember md:w-52"
      style={{ aspectRatio: '2 / 3' }}
    >
      {/* Poster background */}
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(155deg, ${show.cover_from} 0%, ${show.cover_to} 100%)`,
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(120% 80% at 20% 10%, rgba(255,255,255,0.18) 0%, transparent 55%)',
        }}
      />
      {/* Oversized icon as watermark, cropped at the edge */}
      <span
        aria-hidden
        className="absolute -right-6 -bottom-4 select-none text-[7.5rem] opacity-40 transition-transform duration-300 group-hover:scale-110 group-hover:opacity-55"
      >
        {show.cover_icon}
      </span>
      {/* Bottom scrim + text */}
      <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/80 via-black/25 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 p-4">
        <h3 className="font-display text-lg leading-tight font-700 text-white drop-shadow-sm">
          {show.title}
        </h3>
        <p className="mt-1 line-clamp-2 text-xs text-white/70 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          {show.tagline}
        </p>
      </div>
      {/* Voice badge */}
      <span className="absolute top-3 left-3 rounded-full bg-black/45 px-2.5 py-1 text-[11px] font-medium tracking-wide text-white/90 backdrop-blur-sm">
        🎙 {voiceLabel}
      </span>
    </button>
  )
}
