from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
start = text.find('<script>')
end = text.rfind('</script>')
if start == -1 or end == -1 or end <= start:
    raise SystemExit('Failed to find <script> block in index.html')
head = text[: start + len('<script>')]
tail = text[end:]
new_body = '''
const API_ENDPOINT = document.querySelector('meta[name="api-endpoint"]')?.content || '/api/live.json';
const DEFAULT_LIVE_DATA = {
  live: false,
  last_updated: new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC',
  stats: {
    matches_played: 0,
    goals: 0,
    teams: 48,
    host_cities: 16,
  },
  groups: [],
  matches: [],
  scorers: { goals: [], assists: [], shots: [] },
};

const GROUP_PLACEHOLDERS = Array.from({ length: 16 }, (_, index) => ({
  name: `Groupe ${String.fromCharCode(65 + index)}`,
  teams: Array.from({ length: 4 }, (__, teamIndex) => ({
    slot: `${String.fromCharCode(65 + index)}${teamIndex + 1}`,
    name: 'TBD',
    p: 0,
    w: 0,
    d: 0,
    l: 0,
    gf: 0,
    ga: 0,
    pts: 0,
  })),
}));

function formatCountdown(start) {
  if (!start) return 'À venir';
  const target = new Date(start);
  const now = new Date();
  const diff = target - now;
  if (diff <= 0) return 'En cours';
  const days = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  const minutes = Math.floor((diff % 3600000) / 60000);
  return `${days ? days + 'j ' : ''}${hours}h ${minutes}m`;
}

function formatDate(iso) {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function buildGroups(groups = []) {
  const container = document.getElementById('groupsContainer');
  container.innerHTML = '';
  if (!groups.length) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted)">Aucune donnée de groupe disponible</div>';
    return;
  }
  groups.forEach(group => {
    const card = document.createElement('div');
    card.className = 'group-card';
    card.innerHTML = `
      <div class="group-head">${group.name}</div>
      <div class="group-row" style="background:rgba(245,197,24,0.04)">
        <span class="group-col-head">Équipe</span>
        <span class="group-col-head">J</span>
        <span class="group-col-head">G</span>
        <span class="group-col-head">BP</span>
        <span class="group-col-head pts">Pts</span>
      </div>
      ${group.teams.map((team, index) => `
        <div class="group-row ${index < 2 ? 'qualified' : ''}">
          <span>${team.slot} ${team.name}</span>
          <span style="color:var(--muted);font-size:.8rem">${team.p ?? 0}</span>
          <span style="color:var(--muted);font-size:.8rem">${team.w ?? 0}</span>
          <span style="color:var(--muted);font-size:.8rem">${team.gf ?? 0}</span>
          <span class="pts">${team.pts ?? 0}</span>
        </div>
      `).join('')}
    `;
    container.appendChild(card);
  });
}

function renderScorerTable(scorers = []) {
  const body = document.getElementById('scorersBody');
  if (!scorers.length) {
    body.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--muted)">Aucun buteur disponible pour le moment</td></tr>';
    return;
  }
  const max = scorers[0].val || 1;
  body.innerHTML = scorers.map((player, index) => `
    <tr>
      <td class="rank ${index < 3 ? 'top' : ''}">${index + 1}</td>
      <td>
        <div class="player-name">${player.img || '⚽'} ${player.name}</div>
        <div class="player-country">${player.country || ''}</div>
      </td>
      <td>
        <div class="goals-bar-wrap">
          <div class="goals-bar" style="width:${(player.val / max * 160)}px"></div>
          <span class="goals-num">${player.val}</span>
        </div>
      </td>
    </tr>
  `).join('');
}

function buildTimeline(matches = []) {
  const tl = document.getElementById('matchTimeline');
  tl.innerHTML = '';
  if (!matches.length) {
    tl.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted)">Aucun match disponible</div>';
    return;
  }
  matches.slice().sort((a, b) => new Date(a.datetime) - new Date(b.datetime)).forEach(match => {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    const score = match.status === 'finished' ? match.score : 'vs';
    const liveBadge = match.status === 'live' ? '<span class="live-pill live">EN DIRECT</span>' : '';
    const timeLabel = match.status === 'upcoming' && match.datetime ? `<span class="countdown" data-start="${match.datetime}">${formatCountdown(match.datetime)}</span>` : '<span class="countdown">À venir</span>';
    item.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="match-card">
        <span class="match-date">${match.dateLabel || formatDate(match.datetime)}</span>
        <div class="match-teams">
          <span>${match.home}</span>
          <span class="match-score">${score}</span>
          <span>${match.away}</span>
        </div>
        <div class="match-meta">
          <span class="match-stage">${match.stage}${match.group ? ' • ' + match.group : ''}</span>
          ${liveBadge || timeLabel}
        </div>
      </div>
    `;
    tl.appendChild(item);
  });
  updateCountdowns();
  setInterval(updateCountdowns, 1000);
  document.querySelectorAll('.timeline-item').forEach((el, index) => {
    setTimeout(() => el.classList.add('visible'), index * 50);
  });
}

function updateCountdowns() {
  document.querySelectorAll('.countdown[data-start]').forEach(el => {
    el.textContent = formatCountdown(el.dataset.start);
  });
}

function renderLiveSummary(data) {
  const summary = document.getElementById('liveSummary');
  const liveCount = data.matches.filter(match => match.status === 'live').length;
  const upcomingCount = data.matches.filter(match => match.status === 'upcoming').length;
  const finishedCount = data.matches.filter(match => match.status === 'finished').length;
  summary.innerHTML = `${data.live ? 'En direct' : 'A jour'} • En direct: ${liveCount} • À venir: ${upcomingCount} • Terminés: ${finishedCount} • Dernière mise à jour ${data.last_updated}`;
}

function renderHeroCounters(stats) {
  document.querySelectorAll('[data-stat]').forEach(el => {
    const field = el.dataset.stat;
    const value = typeof stats[field] === 'number' ? stats[field] : (field === 'teams' ? 48 : field === 'host_cities' ? 16 : 0);
    el.dataset.target = value;
    el.textContent = '0';
  });
}

function getFallbackScorers(data) {
  if (data.scorers && Array.isArray(data.scorers.goals)) return data.scorers.goals;
  return [];
}

async function fetchLiveData() {
  try {
    const response = await fetch(API_ENDPOINT);
    if (response.ok) return await response.json();
    console.warn('API returned non-ok status', response.status);
  } catch (error) {
    console.warn('Impossible de récupérer l’API live:', error);
  }
  return DEFAULT_LIVE_DATA;
}

function renderLiveBanner(data) {
  const badge = document.getElementById('liveIndicator');
  const info = document.getElementById('heroLiveInfo');
  badge.classList.toggle('live', data.live);
  badge.classList.toggle('offline', !data.live);
  badge.textContent = data.live ? 'STATUT : EN DIRECT' : 'STATUT : HORS LIGNE';
  info.textContent = `Dernière mise à jour : ${data.last_updated}`;
}

function animateCounters() {
  document.querySelectorAll('[data-stat]').forEach(el => {
    const target = parseInt(el.dataset.target, 10) || 0;
    let current = 0;
    const step = Math.max(1, Math.round(target / 60));
    const interval = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toString();
      if (current >= target) clearInterval(interval);
    }, 20);
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const liveData = await fetchLiveData();
  buildGroups(liveData.groups.length ? liveData.groups : GROUP_PLACEHOLDERS);
  renderScorerTable(getFallbackScorers(liveData));
  buildTimeline(liveData.matches);
  renderHeroCounters(liveData.stats);
  renderLiveBanner(liveData);
  renderLiveSummary(liveData);
  setTimeout(animateCounters, 400);
});
'''
path.write_text(head + new_body + tail, encoding='utf-8')
print('wrote', path)
