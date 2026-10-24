// Keep navigation usable from the keyboard without adding remote dependencies.
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.wy-nav-top [data-toggle="wy-nav-top"]');
  const sidebar = document.querySelector('.wy-nav-side');
  if (toggle && sidebar) {
    sidebar.id = sidebar.id || 'guide-navigation';
    toggle.setAttribute('role', 'button');
    toggle.setAttribute('tabindex', '0');
    toggle.setAttribute('aria-label', '打开或关闭文档目录');
    toggle.setAttribute('aria-controls', sidebar.id);
    const update = () => toggle.setAttribute('aria-expanded', String(sidebar.classList.contains('shift')));
    update();
    new MutationObserver(update).observe(sidebar, {attributes: true, attributeFilter: ['class']});
    toggle.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle.click(); }
    });
  }
  const search = document.querySelector('.wy-side-nav-search input[name="q"]');
  if (search) { search.setAttribute('placeholder', '搜索使用手册…'); search.setAttribute('aria-label', '搜索使用手册'); }

  const entryPanel = document.querySelector('[data-live-entry]');
  if (entryPanel) {
    const refresh = entryPanel.querySelector('[data-entry-refresh]');
    const status = entryPanel.querySelector('[data-entry-status]');
    const address = entryPanel.querySelector('[data-entry-address]');
    const stable = 'https://time-reshape.tailfde0f6.ts.net';
    let busy = false, lastAttempt = 0;
    async function updateEntry() {
      if (busy) return;
      busy = true; lastAttempt = Date.now(); refresh.disabled = true;
      status.textContent = '正在获取最新入口…';
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);
      try {
        const response = await fetch(stable + '/api/public/entry', {
          credentials: 'omit', cache: 'no-store', signal: controller.signal,
        });
        if (!response.ok) throw new Error('Unavailable');
        const entry = await response.json();
        if (entry.api_version !== 1 || entry.backup !== stable ||
            !(entry.preferred === stable || /^https:\/\/[a-z0-9]+(?:-[a-z0-9]+)*\.trycloudflare\.com$/.test(entry.preferred))) throw new Error('Invalid entry');
        address.textContent = entry.preferred;
        status.textContent = entry.accelerated ? '已获取当前加速入口' : '加速入口正在准备，可通过备用入口访问';
        entryPanel.dataset.state = entry.accelerated ? 'ready' : 'fallback';
      } catch {
        address.textContent = '';
        status.textContent = '暂时无法获取入口。可点击上方按钮重试，或使用备用下载入口。';
        entryPanel.dataset.state = 'unavailable';
      } finally {
        clearTimeout(timeout); busy = false; refresh.disabled = false;
      }
    }
    refresh.addEventListener('click', () => void updateEntry());
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && Date.now() - lastAttempt > 5000) void updateEntry();
    });
    setInterval(() => { if (!document.hidden) void updateEntry(); }, 60000);
    void updateEntry();
  }
});
