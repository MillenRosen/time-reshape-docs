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
});
