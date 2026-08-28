"""Internal dashboard metrics.

Mocked usage data (60 days, deterministic) modeling the product thesis, with
KPIs mirroring what real audio platforms measure (Spotify for Creators: plays
>=30s vs unique listeners, followers; Apple Podcasts: engaged listeners >=40%;
YouTube: retention/drop-off curve). Shared daily editions mean cost scales
with content, not users; episodes still relevant carry over from the previous
day and are NOT regenerated — both effects show up as savings. Real generation
costs from the usage_log ledger are blended in (the "live" panel).
"""

import random
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Episode, Story, UsageLog
from ..services import llm
from ..services.discovery import content_language

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

CATEGORY_SHARE = {
    "tech": 0.32, "finance": 0.18, "spain": 0.15, "us": 0.14,
    "history": 0.12, "colombia": 0.09,
}
SUBSCRIPTION_EUR = 4.99
DAYS = 60
EPISODES_PER_DAY = 6 * 8  # categories x daily stories (shared editions)

# Listening by hour of day (share of daily plays) — commute + evening peaks.
HOUR_PROFILE = [
    0.2, 0.1, 0.1, 0.1, 0.3, 1.2, 3.8, 7.5, 8.6, 5.2, 3.4, 3.0,
    3.6, 3.2, 2.6, 2.8, 3.6, 5.4, 7.8, 9.4, 8.9, 6.8, 4.6, 1.9,
]


def _mock_series() -> list[dict]:
    rng = random.Random(42)
    series = []
    users = 120.0
    paid_ratio = 0.045
    today = date.today()
    for i in range(DAYS):
        day = today - timedelta(days=DAYS - 1 - i)
        growth = 1.0 + rng.uniform(0.025, 0.06) * (1.0 if day.weekday() < 5 else 0.4)
        users *= growth
        paid_ratio = min(0.085, paid_ratio + rng.uniform(0.0002, 0.0009))
        dau = users * rng.uniform(0.30, 0.40)
        listeners = dau * rng.uniform(0.82, 0.95)      # unique listeners
        plays = listeners * rng.uniform(1.6, 2.1)      # plays >= 30s (Spotify model)
        avg_min = rng.uniform(7.4, 9.1)

        # Shared editions: some of yesterday's episodes stay relevant and are
        # reused instead of regenerated — direct savings.
        reused = round(EPISODES_PER_DAY * rng.uniform(0.22, 0.42))
        generated = EPISODES_PER_DAY - reused
        # Paid users' custom episodes generate on top (per-user cost).
        custom = round(users * paid_ratio * rng.uniform(0.25, 0.45))

        llm_cost = (generated + custom) * rng.uniform(0.010, 0.016)
        tts_cost = (generated + custom) * rng.uniform(0.55, 0.75) * 0.35
        series.append({
            "date": day.isoformat(),
            "users": round(users),
            "paid_users": round(users * paid_ratio),
            "dau": round(dau),
            "listeners": round(listeners),
            "plays": round(plays),
            "minutes": round(plays * avg_min),
            "avg_minutes_per_listen": round(avg_min, 1),
            "generated": generated,
            "reused": reused,
            "custom": custom,
            "llm_cost": round(llm_cost, 2),
            "tts_cost": round(tts_cost, 2),
        })
    return series


def _retention_curve() -> list[dict]:
    """Avg % of audience still listening at each % of the episode (YouTube-style)."""
    rng = random.Random(7)
    curve, audience = [], 100.0
    for pct in range(0, 105, 5):
        if pct == 0:
            audience = 100.0
        elif pct <= 10:
            audience -= rng.uniform(6, 9)      # intro drop
        elif pct < 85:
            audience -= rng.uniform(1.0, 2.2)  # steady body
        else:
            audience -= rng.uniform(2.5, 4.0)  # outro drop
        curve.append({"pct": pct, "audience": round(max(audience, 0), 1)})
    return curve


def _cohorts() -> list[dict]:
    """Weekly signup cohorts with retention triangle (Amplitude/Mixpanel style)."""
    rng = random.Random(5)
    today = date.today()
    cohorts = []
    for w in range(8):
        start = today - timedelta(days=(8 - w) * 7)
        size = round(58 * (1.32 ** w) * rng.uniform(0.85, 1.15))
        weeks: list[float] = []
        for k in range(9 - w):
            if k == 0:
                weeks.append(100.0)
            elif k == 1:
                # Later cohorts retain better (product improving) — the story
                # an investor wants to see in a cohort triangle.
                weeks.append(round(rng.uniform(36, 42) + w * 1.1, 1))
            else:
                weeks.append(round(weeks[-1] * rng.uniform(0.80, 0.91), 1))
        cohorts.append({"cohort": start.isoformat(), "size": size, "weeks": weeks})
    return cohorts


def _episode_stats(s: Story) -> dict:
    """Deterministic per-episode mock stats seeded by story id (stable across
    reloads, like real data); duration is real when the episode exists.
    Includes YouTube-Studio-style most-replayed / most-skipped moments."""
    rng = random.Random(s.id * 977)
    plays = round(rng.uniform(60, 640))
    listeners = round(plays * rng.uniform(0.55, 0.80))

    curve, audience = [], 100.0
    hook_drop = rng.uniform(3, 13)   # how much the intro loses
    body_rate = rng.uniform(0.7, 2.1)
    for pct in range(0, 105, 5):
        if pct == 0:
            audience = 100.0
        elif pct <= 10:
            audience -= hook_drop / 2 * rng.uniform(0.7, 1.3)
        elif pct < 85:
            audience -= body_rate * rng.uniform(0.7, 1.3)
        else:
            audience -= rng.uniform(1.5, 4.0)
        curve.append({"pct": pct, "audience": round(max(audience, 5), 1)})

    # Most-replayed: a bump in the curve where people scrub back.
    replay_idx = rng.randrange(4, 15)  # 20%..70%
    bump = rng.uniform(2.5, 6.0)
    curve[replay_idx]["audience"] = round(curve[replay_idx]["audience"] + bump, 1)
    if replay_idx + 1 < len(curve):
        curve[replay_idx + 1]["audience"] = round(curve[replay_idx + 1]["audience"] + bump / 2, 1)
    most_replayed_pct = curve[replay_idx]["pct"]

    # Most-skipped: the steepest audience drop after the intro.
    drops = [
        (curve[i]["audience"] - curve[i + 1]["audience"], curve[i]["pct"])
        for i in range(3, len(curve) - 1)
    ]
    most_skipped_pct = max(drops)[1]

    daily = [
        {"day": f"D{i}", "plays": round(plays * share * rng.uniform(0.85, 1.15))}
        for i, share in enumerate([0.38, 0.24, 0.13, 0.09, 0.07, 0.05, 0.04])
    ]
    episode = s.episodes[0] if s.episodes else None
    return {
        "story_id": s.id,
        "title": s.title,
        "category": s.category.slug if s.category else "",
        "status": s.status.value,
        "duration_s": episode.duration_s if episode else None,
        "plays": plays,
        "listeners": listeners,
        "completion": round(curve[-1]["audience"] / 100, 2),
        "most_replayed_pct": most_replayed_pct,
        "most_skipped_pct": most_skipped_pct,
        "retention": curve,
        "daily": daily,
    }


@router.get("/episodes")
def episode_metrics(db: Session = Depends(get_db)):
    """Per-episode stats, YouTube-Studio style: pick an episode, see ITS curve."""
    stories = (
        db.query(Story)
        .filter(Story.language == content_language(db))
        .order_by(Story.id.desc())
        .limit(30)
        .all()
    )
    return [_episode_stats(s) for s in stories]


_ANALYZE_SYSTEM = """Eres el analista de contenido de un servicio de podcasts generados con IA.
Recibes las estadísticas de UN episodio (curva de retención, momento más repetido,
momento más saltado, completado, decay de plays) y, si existe, el fragmento del guion
en esos momentos. Explica qué está pasando y qué haría el equipo de contenido.

Devuelve JSON: {"insights": ["3-4 frases-hallazgo, concretas y accionables"],
"recommendation": "una recomendación principal en 1-2 frases"}
Tono: analista senior, directo, sin relleno. En el idioma del guion/estadísticas."""


def _script_at(episode, pct: float) -> str:
    if not episode or not episode.script:
        return "(sin guion disponible)"
    lines = episode.script
    idx = min(int(pct / 100 * len(lines)), len(lines) - 1)
    excerpt = [l["text"] for l in lines[max(0, idx - 1): idx + 2]]
    return " / ".join(excerpt)[:500]


@router.post("/episodes/{story_id}/analyze")
def analyze_episode(story_id: int, db: Session = Depends(get_db)):
    """One GPT-5.6 Sol call: turn this episode's stats into editorial insights."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    stats = _episode_stats(story)
    episode = story.episodes[0] if story.episodes else None

    curve_txt = ", ".join(f"{p['pct']}%:{p['audience']}%" for p in stats["retention"])
    user = (
        f"EPISODIO: {stats['title']} (categoría {stats['category']})\n"
        f"Plays: {stats['plays']} · Oyentes únicos: {stats['listeners']} · "
        f"Completado: {stats['completion']:.0%}\n"
        f"CURVA DE RETENCIÓN (posición:audiencia): {curve_txt}\n"
        f"MOMENTO MÁS REPETIDO: {stats['most_replayed_pct']}% — guion ahí: "
        f"«{_script_at(episode, stats['most_replayed_pct'])}»\n"
        f"MOMENTO MÁS SALTADO: {stats['most_skipped_pct']}% — guion ahí: "
        f"«{_script_at(episode, stats['most_skipped_pct'])}»\n"
        f"PLAYS POR DÍA: {stats['daily']}"
    )
    from ..config import settings

    data = llm.chat_json(
        _ANALYZE_SYSTEM, user, model=settings.script_model, kind="analysis", meta=stats["category"]
    )
    return {
        "insights": [str(i) for i in data.get("insights", [])][:5],
        "recommendation": str(data.get("recommendation", "")),
    }


@router.get("")
def metrics(db: Session = Depends(get_db)):
    series = _mock_series()
    last = series[-1]
    last7 = series[-7:]
    mau = last["users"]
    plays_day = round(sum(d["plays"] for d in last7) / 7)
    listeners_day = round(sum(d["listeners"] for d in last7) / 7)
    daily_cost_avg = sum(d["llm_cost"] + d["tts_cost"] for d in last7) / 7
    generations_7d = sum(d["generated"] + d["custom"] for d in last7)
    cost_7d = sum(d["llm_cost"] + d["tts_cost"] for d in last7)
    cost_total = sum(d["llm_cost"] + d["tts_cost"] for d in series)
    reused_total = sum(d["reused"] for d in series)
    cost_per_generation = cost_7d / generations_7d
    savings_reuse = round(reused_total * cost_per_generation, 2)
    cost_per_listener_month = daily_cost_avg * 30 / mau

    hourly_total = sum(HOUR_PROFILE)
    hourly = [
        {"hour": f"{h:02d}", "plays": round(plays_day * share / hourly_total)}
        for h, share in enumerate(HOUR_PROFILE)
    ]
    peak_hour = max(range(24), key=lambda h: HOUR_PROFILE[h])

    per_category = [
        {
            "category": slug,
            "listens": round(sum(d["plays"] for d in series) * share),
            "cost_per_episode": round(cost_per_generation * (0.8 + share), 3),
        }
        for slug, share in CATEGORY_SHARE.items()
    ]

    # Top episodes: real story titles from this instance (one per category so
    # the table reads like a catalog), mock listen numbers.
    rng = random.Random(11)
    recent = (
        db.query(Story)
        .filter(Story.title != "", Story.language == content_language(db))
        .order_by(Story.id.desc())
        .limit(30)
        .all()
    )
    top_stories, seen_cats = [], set()
    for s in recent:
        cat = s.category.slug if s.category else ""
        if cat not in seen_cats:
            top_stories.append(s)
            seen_cats.add(cat)
        if len(top_stories) == 5:
            break
    top_episodes = [
        {
            "title": s.title,
            "category": s.category.slug if s.category else "",
            "plays": round(plays_day * rng.uniform(0.10, 0.32)),
            "completion": round(rng.uniform(0.58, 0.87), 2),
        }
        for s in top_stories
    ]
    top_episodes.sort(key=lambda e: e["plays"], reverse=True)

    real_rows = (
        db.query(UsageLog.kind, func.count(), func.sum(UsageLog.cost_usd),
                 func.sum(UsageLog.input_tokens + UsageLog.output_tokens),
                 func.sum(UsageLog.characters))
        .group_by(UsageLog.kind)
        .all()
    )
    episodes_real = db.query(func.count(Episode.id)).scalar() or 0
    avg_duration_real = db.query(func.avg(Episode.duration_s)).scalar()

    return {
        "series": series,
        "retention": _retention_curve(),
        "cohorts": _cohorts(),
        "hourly": hourly,
        "per_category": per_category,
        "top_episodes": top_episodes,
        "kpis": {
            "mau": mau,
            "paid_users": last["paid_users"],
            "paid_pct": round(last["paid_users"] / mau, 3),
            "plays_day": plays_day,
            "listeners_day": listeners_day,
            "engaged_pct": 0.61,   # listened >=40% of the episode (Apple-style)
            "completion": 0.74,
            "avg_minutes_per_listen": last["avg_minutes_per_listen"],
            "peak_hour": f"{peak_hour:02d}:00",
            "cost_per_generation": round(cost_per_generation, 3),
            "cost_per_user_day": round(daily_cost_avg / mau, 4),
            "cost_per_listener_month": round(cost_per_listener_month, 3),
            "gross_margin": round(1 - cost_per_listener_month / SUBSCRIPTION_EUR, 3),
            "savings_reuse": savings_reuse,
            "cost_total": round(cost_total, 2),
        },
        "real": {
            "by_kind": [
                {
                    "kind": kind,
                    "calls": calls,
                    "cost_usd": round(cost or 0, 4),
                    "tokens": int(tokens or 0),
                    "characters": int(chars or 0),
                }
                for kind, calls, cost, tokens, chars in real_rows
            ],
            "episodes": episodes_real,
            "avg_episode_minutes": round((avg_duration_real or 0) / 60, 1),
        },
    }
