(() => {
  const key = 'runner-theme';
  const normalize = value => value === 'dark' ? 'dark' : 'light';
  function apply(value) {
    const theme = normalize(value);
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      const label = theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme';
      button.setAttribute('aria-pressed', String(theme === 'dark'));
      button.setAttribute('aria-label', label);
      button.setAttribute('title', label);
    });
  }
  let saved;
  try { saved = localStorage.getItem(key); } catch (_) { /* Storage can be blocked. */ }
  apply(saved);
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.addEventListener('click', () => {
        const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        apply(theme);
        try { localStorage.setItem(key, theme); } catch (_) { /* Keep the current page usable. */ }
      });
    });
  });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) apply(event.newValue);
  });
})();
