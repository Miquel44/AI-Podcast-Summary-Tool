import { useEffect, useRef, useState } from 'react'
import type { Episode, Story } from '../types'

function fmt(seconds: number) {
  if (!Number.isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export interface NowPlaying {
  story: Story
  episode: Episode
}

export function PlayerBar({
  nowPlaying,
  onClose,
  onOpenStory,
}: {
  nowPlaying: NowPlaying
  onClose: () => void
  onOpenStory: (story: Story) => void
}) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [playing, setPlaying] = useState(true)
  const [time, setTime] = useState(0)
  const [duration, setDuration] = useState(nowPlaying.episode.duration_s ?? 0)
  const [volume, setVolume] = useState(1)

  const { story, episode } = nowPlaying

  // Autoplay on track change.
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    audio.play().catch(() => setPlaying(false))
    setPlaying(true)
  }, [episode.id])

  const toggle = () => {
    const audio = audioRef.current
    if (!audio) return
    if (audio.paused) {
      audio.play()
      setPlaying(true)
    } else {
      audio.pause()
      setPlaying(false)
    }
  }

  const seek = (value: number) => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = value
    setTime(value)
  }

  const skip = (delta: number) => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = Math.max(0, Math.min(audio.currentTime + delta, duration))
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-ink-soft/95 backdrop-blur-md">
      <audio
        ref={audioRef}
        src={episode.audio_path ?? undefined}
        onTimeUpdate={(e) => setTime(e.currentTarget.currentTime)}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
        onEnded={() => setPlaying(false)}
      />
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-1.5 md:px-6">
        {/* Track info */}
        <button
          onClick={() => onOpenStory(story)}
          className="flex min-w-0 flex-1 cursor-pointer items-center gap-2.5 text-left md:flex-none md:basis-72"
        >
          <div
            className="h-9 w-9 shrink-0 overflow-hidden rounded-md"
            style={{
              background: `linear-gradient(140deg, ${story.cover_from}, ${story.cover_to})`,
            }}
          >
            {story.cover_image && (
              <img src={story.cover_image} alt="" className="h-full w-full object-cover" />
            )}
          </div>
          <div className="min-w-0">
            <p className="truncate text-[13px] leading-tight font-semibold text-white">
              {episode.title || story.title}
            </p>
            <p className="truncate text-[11px] leading-tight text-white/45">{story.tagline}</p>
          </div>
        </button>

        {/* Controls + progress, single compact row */}
        <div className="flex flex-1 items-center justify-center gap-3">
          <button
            onClick={() => skip(-15)}
            aria-label="-15s"
            className="cursor-pointer text-[11px] font-semibold text-white/50 transition hover:text-white"
          >
            ⟲ 15
          </button>
          <button
            onClick={toggle}
            aria-label={playing ? 'Pause' : 'Play'}
            className="flex h-7 w-7 shrink-0 cursor-pointer items-center justify-center rounded-full bg-white text-xs text-ink transition hover:scale-105"
          >
            {playing ? '❚❚' : '▶'}
          </button>
          <button
            onClick={() => skip(15)}
            aria-label="+15s"
            className="cursor-pointer text-[11px] font-semibold text-white/50 transition hover:text-white"
          >
            15 ⟳
          </button>
          <div className="hidden w-full max-w-md items-center gap-2 md:flex">
            <span className="w-10 text-right text-[11px] text-white/40" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {fmt(time)}
            </span>
            <input
              type="range"
              min={0}
              max={duration || 0}
              step={1}
              value={time}
              onChange={(e) => seek(Number(e.target.value))}
              className="player-range h-1 flex-1 cursor-pointer"
            />
            <span className="w-10 text-[11px] text-white/40" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {fmt(duration)}
            </span>
          </div>
        </div>

        {/* Volume + close */}
        <div className="hidden items-center gap-3 md:flex md:basis-40 md:justify-end">
          <span aria-hidden className="text-xs text-white/40">🔊</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={volume}
            onChange={(e) => {
              const v = Number(e.target.value)
              setVolume(v)
              if (audioRef.current) audioRef.current.volume = v
            }}
            className="player-range h-1 w-20 cursor-pointer"
          />
          <button
            onClick={onClose}
            aria-label="Cerrar reproductor"
            className="cursor-pointer text-white/40 transition hover:text-white"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}
