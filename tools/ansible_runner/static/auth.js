window.runnerRole = document.querySelector('meta[name="runner-role"]')?.content || 'viewer';
window.runnerFetch = async function (url, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  if (token) headers.set('X-CSRF-Token', token);
  const response = await fetch(url, {...options, headers, credentials: 'same-origin'});
  if (response.status === 401) window.location.assign('/login');
  return response;
};
