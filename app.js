/* Local page controls. No framework, server, or network request is required. */
(() => {
  'use strict';
  const root = document.getElementById('simpaisa-review-v26');
  if (!root) return;
  const pages = [...root.querySelectorAll('.page-preview[data-preview]')];
  const pageNumbers = pages.map(page => Number(page.dataset.preview));
  const selector = root.querySelector('#simpaisa-v26-page');
  const previous = root.querySelector('#simpaisa-v26-previous');
  const next = root.querySelector('#simpaisa-v26-next');
  const counter = root.querySelector('#simpaisa-v26-counter');
  const guides = root.querySelector('#simpaisa-v26-guides');
  let current = pageNumbers[0];

  function resizePages() {
    const scale = root.getBoundingClientRect().width / 595;
    for (const preview of pages) {
      preview.querySelector('.book-page').style.transform = `scale(${scale})`;
      preview.style.height = `${842 * scale}px`;
    }
  }

  function showPage(value) {
    const requested = Number(value);
    current = pageNumbers.includes(requested) ? requested : pageNumbers[0];
    if (selector) selector.value = String(current);
    for (const page of pages) page.hidden = Number(page.dataset.preview) !== current;
    for (const note of root.querySelectorAll('[data-notes-for]')) {
      note.hidden = Number(note.dataset.notesFor) !== current;
    }
    if (previous) previous.disabled = current === pageNumbers[0];
    if (next) next.disabled = current === pageNumbers[pageNumbers.length - 1];
    if (counter) counter.textContent = `${current} / 13`;
    resizePages();
  }

  function readHash() {
    const match = location.hash.match(/^#page-(\d+)$/);
    showPage(match ? match[1] : pageNumbers[0]);
  }

  function navigate(value) {
    if (pageNumbers.includes(value)) location.hash = `page-${value}`;
  }

  selector?.addEventListener('change', () => navigate(Number(selector.value)));
  previous?.addEventListener('click', () => navigate(pageNumbers[pageNumbers.indexOf(current) - 1]));
  next?.addEventListener('click', () => navigate(pageNumbers[pageNumbers.indexOf(current) + 1]));
  guides?.addEventListener('change', () => root.classList.toggle('show-guides', guides.checked));
  window.addEventListener('hashchange', readHash);
  window.addEventListener('keydown', event => {
    if (event.target.closest('input, select, textarea, button') || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowLeft') navigate(pageNumbers[pageNumbers.indexOf(current) - 1]);
    if (event.key === 'ArrowRight') navigate(pageNumbers[pageNumbers.indexOf(current) + 1]);
  });
  new ResizeObserver(resizePages).observe(root);
  document.fonts.ready.then(resizePages);
  readHash();
})();
