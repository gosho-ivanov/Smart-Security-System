/* Smart Security System — main.js */

// ── Active nav link highlight ──
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash messages after 5s
  document.querySelectorAll('.alert-box').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // Topbar notification button
  const notifBtn = document.querySelector('.topbar-icon-btn');
  if (notifBtn) {
    notifBtn.addEventListener('click', () => {
      const dot = notifBtn.querySelector('.notif-dot');
      if (dot) dot.style.display = 'none';
    });
  }
});
