document.querySelectorAll('textarea[name="answer"]').forEach((area) => {
  area.addEventListener('input', () => {
    area.setAttribute('aria-label', `Interview answer, ${area.value.trim().split(/\s+/).filter(Boolean).length} words`);
  });
});
