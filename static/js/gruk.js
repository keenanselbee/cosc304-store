// keep gruk chatting while the shop is open
(() => {
  const quote = document.querySelector('#gruk-quote');
  if (!quote) return;
  const defaultQuote = quote.textContent.trim();
  const quotes = [defaultQuote,
    'You bring ears. Gruk brings gear. Good arrangement.',
    'Browse all you want. Touch cursed shelf at own risk.',
    'That dent? Premium dent.',
    'Sharp end goes away from customer. Usually.',
    'Gruk tested the shield. Wall lost.',
    'No haggling. Gruk already argued with price tag.'];
  const pitches = {
    1: 'Slightly used. Other fellow barely got a turn.',
    2: 'Two blades. Finally, both sides of an argument.',
    3: 'Every dent is an attack you do not have to catch.',
    4: 'Protects head. Good ideas sold separately.',
    5: 'Run away faster. Gruk calls that a winning feature.',
    6: 'Warm feeling guaranteed. Eyebrows not guaranteed.',
    7: 'Two thoughts per bottle. Do not drink before bed.',
    8: 'Warning label costs extra. This one has it free.'};
  const pitchCooldown = 6000;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const bubble = quote.closest('.speech-bubble');
  let timer;
  let pool = [];
  let current = defaultQuote;
  let typing = false;
  let nextPitchAt = 0;

  function stop() {
    clearTimeout(timer);
    typing = false;
    bubble.classList.add('paused');
    quote.querySelectorAll('.quote-letter').forEach(letter => letter.style.visibility = 'visible');
  }
  function nextQuote() {
    if (!pool.length) {
      pool = [...quotes];
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
      }
      if (pool[0] === current) [pool[0], pool[1]] = [pool[1], pool[0]];
    }
    show(pool.shift());
  }
  function schedule() {
    if (!reducedMotion.matches && !document.hidden) {
      bubble.classList.remove('paused');
      timer = setTimeout(nextQuote, 10000);
    }
  }
  function show(text) {
    clearTimeout(timer);
    typing = true;
    current = text;
    quote.replaceChildren();
    const accessible = document.createElement('span');
    accessible.className = 'sr-only';
    accessible.textContent = text;
    const visual = document.createElement('span');
    visual.setAttribute('aria-hidden', 'true');
    const letters = [];
    text.split(/(\s+)/).forEach(word => {
      if (/^\s+$/.test(word)) { visual.append(document.createTextNode(word)); return; }
      const group = document.createElement('span');
      group.className = 'quote-word';
      for (const character of word) {
        const letter = document.createElement('span');
        letter.className = 'quote-letter';
        letter.textContent = character;
        letter.style.visibility = 'hidden';
        letter.style.setProperty('--delay', `${-Math.random() * 700}ms`);
        group.append(letter);
        letters.push(letter);
      }
      visual.append(group);
    });
    quote.append(accessible, visual);
    bubble.classList.remove('paused');
    let index = 0;
    function type() {
      if (reducedMotion.matches || document.hidden) { stop(); return; }
      if (index < letters.length) {
        letters[index++].style.visibility = 'visible';
        timer = setTimeout(type, 25);
      } else {
        typing = false;
        schedule();
      }
    }
    type();
  }
  function motionChanged() {
    stop();
    if (reducedMotion.matches) {
      current = defaultQuote;
      quote.textContent = defaultQuote;
    } else {
      show(defaultQuote);
    }
  }
  function pitch(card) {
    if (typing || reducedMotion.matches || document.hidden || Date.now() < nextPitchAt) return;
    const text = pitches[card.dataset.productId];
    if (!text || text === current) return;
    nextPitchAt = Date.now() + pitchCooldown;
    show(text);
  }
  document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('pointerenter', () => pitch(card));
    card.addEventListener('focusin', event => {
      if (!card.contains(event.relatedTarget)) pitch(card);
    });
  });
  document.addEventListener('visibilitychange', () => { stop(); if (!document.hidden) schedule(); });
  reducedMotion.addEventListener('change', motionChanged);
  motionChanged();
})();
