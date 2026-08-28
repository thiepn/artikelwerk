(() => {
  'use strict';

  const SHELL_ID = 'aw-practice-shell';
  const LAUNCH_ID = 'aw-practice-launch';
  const OPEN_CLASS = 'aw-practice-open';
  const ROOT_CLASS = 'aw-practice-root';
  const CACHE_KEY = 'artikelwerk:english-cache:v1';
  const TRIGGER_WORDS = ['üben', 'practice', 'practise', 'trainer', 'training', 'quiz'];
  const ARTICLE_WORDS = new Set(['der', 'die', 'das']);
  const IGNORED_PROMPT_WORDS = new Set([
    'artikel', 'welcher', 'welche', 'welches', 'wähle', 'wählen', 'richtige',
    'richtigen', 'richtig', 'antwort', 'frage', 'nomen', 'wort', 'übung',
    'practice', 'choose', 'select', 'answer', 'german', 'deutsch', 'weiter',
    'nächste', 'noch', 'einmal', 'bedeutung', 'definition'
  ]);

  const state = {
    open: false,
    root: null,
    originalParent: null,
    originalNextSibling: null,
    launcher: null,
    shell: null,
    mount: null,
    translationEl: null,
    explanationEl: null,
    progressEl: null,
    statusEl: null,
    returnFocus: null,
    scrollY: 0,
    savedBodyStyle: null,
    savedHtmlStyle: null,
    observer: null,
    resizeObserver: null,
    updateFrame: 0,
    translationSequence: 0,
    translationAbort: null,
    answered: 0,
    translationIndex: null,
    cache: null,
    originalScrollIntoView: Element.prototype.scrollIntoView,
    originalScrollTo: window.scrollTo.bind(window),
    originalScrollBy: window.scrollBy.bind(window)
  };

  const normalize = (value) => String(value ?? '')
    .replace(/\u00ad/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  const normalizeKey = (value) => normalize(value)
    .toLocaleLowerCase('de-DE')
    .replace(/^[\s"'„“‚‘([{]+|[\s"'”’.,!?;:…\])}]+$/g, '');

  const isVisible = (element) => {
    if (!(element instanceof Element)) return false;
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const elementText = (element) => normalize(
    element instanceof HTMLInputElement ? element.value : element?.textContent
  );

  const exactArticle = (element) => ARTICLE_WORDS.has(normalizeKey(elementText(element)));

  function getArticleChoices(scope = document, visibleOnly = false) {
    return Array.from(scope.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'))
      .filter((element) => exactArticle(element))
      .filter((element) => !visibleOnly || isVisible(element));
  }

  function commonAncestor(elements) {
    if (!elements.length) return null;
    let candidate = elements[0];
    while (candidate && !elements.every((element) => candidate.contains(element))) {
      candidate = candidate.parentElement;
    }
    return candidate;
  }

  function rootScore(element) {
    if (!(element instanceof HTMLElement) || element === document.body || element === document.documentElement) return -Infinity;
    const articleChoices = getArticleChoices(element);
    const articles = new Set(articleChoices.map((choice) => normalizeKey(elementText(choice))));
    if (articles.size < 3) return -Infinity;

    const text = normalizeKey(element.textContent);
    const rect = element.getBoundingClientRect();
    let score = 100;
    score -= Math.min(40, articleChoices.length * 2);
    score -= Math.min(25, element.querySelectorAll('*').length / 15);
    if (/artikel|nomen|wort|übung|practice|trainer|frage|question/.test(text)) score += 22;
    if (/definition|bedeutung|meaning|explanation|erklärung|richtig|falsch/.test(text)) score += 12;
    if (element.matches('section, article, form, [class*="card" i], [class*="practice" i], [class*="quiz" i], [id*="practice" i], [id*="quiz" i]')) score += 18;
    if (rect.width > 0 && rect.height > 0) score += 10;
    if (rect.height > window.innerHeight * 1.5) score -= 45;
    if (element.closest(`#${SHELL_ID}`)) score += 10;
    return score;
  }

  function findPracticeRoot() {
    const allChoices = getArticleChoices(document);
    if (!allChoices.length) return null;

    const groups = [];
    const visible = allChoices.filter(isVisible);
    const source = visible.length >= 3 ? visible : allChoices;
    const byArticle = ['der', 'die', 'das'].map((article) => source.filter((choice) => normalizeKey(elementText(choice)) === article));

    for (const der of byArticle[0].slice(0, 8)) {
      for (const die of byArticle[1].slice(0, 8)) {
        for (const das of byArticle[2].slice(0, 8)) {
          const common = commonAncestor([der, die, das]);
          if (!common) continue;
          let candidate = common;
          for (let depth = 0; candidate && depth < 6; depth += 1, candidate = candidate.parentElement) {
            if (candidate === document.body || candidate === document.documentElement) break;
            groups.push(candidate);
          }
        }
      }
    }

    const unique = [...new Set(groups)];
    unique.sort((a, b) => rootScore(b) - rootScore(a));
    return unique[0] || null;
  }

  function triggerScore(element) {
    if (!(element instanceof HTMLElement) || element.id === LAUNCH_ID || element.closest(`#${SHELL_ID}`)) return -Infinity;
    const text = normalizeKey(elementText(element));
    if (!text) return -Infinity;
    const matched = TRIGGER_WORDS.find((word) => text === word || text.includes(word));
    if (!matched) return -Infinity;
    let score = text === matched ? 50 : 30;
    if (isVisible(element)) score += 25;
    if (element.matches('button, a, [role="button"], [role="tab"]')) score += 15;
    if (element.getAttribute('aria-current') || element.getAttribute('aria-selected') === 'true') score += 5;
    return score;
  }

  function findPracticeTrigger() {
    return Array.from(document.querySelectorAll('button, a, [role="button"], [role="tab"], input[type="button"], input[type="submit"]'))
      .map((element) => ({ element, score: triggerScore(element) }))
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score)[0]?.element || null;
  }

  function createShell() {
    const existing = document.getElementById(SHELL_ID);
    if (existing) {
      state.shell = existing;
      state.mount = existing.querySelector('.aw-practice-mount');
      state.translationEl = existing.querySelector('.aw-practice-translation');
      state.explanationEl = existing.querySelector('.aw-practice-explanation');
      state.progressEl = existing.querySelector('.aw-practice-progress');
      state.statusEl = existing.querySelector('.aw-practice-status');
      return existing;
    }

    const shell = document.createElement('section');
    shell.id = SHELL_ID;
    shell.hidden = true;
    shell.setAttribute('role', 'dialog');
    shell.setAttribute('aria-modal', 'true');
    shell.setAttribute('aria-labelledby', 'aw-practice-title');
    shell.innerHTML = `
      <header class="aw-practice-header">
        <button class="aw-practice-close" type="button" aria-label="Close practice">×</button>
        <div class="aw-practice-heading">
          <strong id="aw-practice-title">Article practice</strong>
          <span>Choose der, die, or das. Everything stays on this screen.</span>
        </div>
        <div class="aw-practice-progress" aria-label="Practice progress">0</div>
      </header>
      <div class="aw-practice-stage">
        <main class="aw-practice-mount" aria-live="off"></main>
        <aside class="aw-practice-support" aria-label="English support">
          <section class="aw-practice-support-section">
            <p class="aw-practice-support-label">English meaning</p>
            <p class="aw-practice-translation">Open a question to see the translation.</p>
          </section>
          <section class="aw-practice-support-section">
            <p class="aw-practice-support-label">Explanation in English</p>
            <p class="aw-practice-explanation">Feedback and definitions remain here without moving the page.</p>
          </section>
        </aside>
      </div>
      <p class="aw-practice-status" aria-live="polite"></p>
    `;
    document.body.append(shell);

    state.shell = shell;
    state.mount = shell.querySelector('.aw-practice-mount');
    state.translationEl = shell.querySelector('.aw-practice-translation');
    state.explanationEl = shell.querySelector('.aw-practice-explanation');
    state.progressEl = shell.querySelector('.aw-practice-progress');
    state.statusEl = shell.querySelector('.aw-practice-status');

    shell.querySelector('.aw-practice-close').addEventListener('click', closePractice);
    shell.addEventListener('click', (event) => {
      const choice = event.target.closest('[data-aw-article-choice]');
      if (!choice) return;
      state.answered += 1;
      updateProgress();
      queueSupportUpdate();
    }, true);

    return shell;
  }

  function createLauncher() {
    const existing = document.getElementById(LAUNCH_ID);
    if (existing) {
      state.launcher = existing;
      return existing;
    }

    const launcher = document.createElement('button');
    launcher.id = LAUNCH_ID;
    launcher.type = 'button';
    launcher.setAttribute('aria-haspopup', 'dialog');
    launcher.setAttribute('aria-controls', SHELL_ID);
    launcher.innerHTML = '<span aria-hidden="true">▶</span><span>Practice</span>';
    launcher.addEventListener('click', () => openPractice());

    const trigger = findPracticeTrigger();
    const host = trigger?.closest('nav, header, [role="navigation"], [class*="toolbar" i], [class*="actions" i]');
    if (host && isVisible(host)) {
      if (trigger.parentElement === host) trigger.insertAdjacentElement('afterend', launcher);
      else host.append(launcher);
    } else {
      launcher.classList.add('aw-practice-launch--floating');
      document.body.append(launcher);
    }

    state.launcher = launcher;
    return launcher;
  }

  function setViewportHeight() {
    document.documentElement.style.setProperty('--aw-practice-vh', `${window.innerHeight}px`);
  }

  function saveInlineStyle(element) {
    return element.getAttribute('style');
  }

  function restoreInlineStyle(element, value) {
    if (value === null) element.removeAttribute('style');
    else element.setAttribute('style', value);
  }

  function lockPage() {
    state.scrollY = window.scrollY || document.documentElement.scrollTop || 0;
    state.savedBodyStyle = saveInlineStyle(document.body);
    state.savedHtmlStyle = saveInlineStyle(document.documentElement);
    document.documentElement.classList.add(OPEN_CLASS);
    document.body.classList.add(OPEN_CLASS);
    document.body.style.top = `${-state.scrollY}px`;
  }

  function unlockPage() {
    document.documentElement.classList.remove(OPEN_CLASS);
    document.body.classList.remove(OPEN_CLASS);
    restoreInlineStyle(document.body, state.savedBodyStyle);
    restoreInlineStyle(document.documentElement, state.savedHtmlStyle);
    state.originalScrollTo(0, state.scrollY);
  }

  function installScrollGuards() {
    if (Element.prototype.scrollIntoView.__awPracticeGuard) return;

    const guardedScrollIntoView = function guardedScrollIntoView(...args) {
      if (state.open) return undefined;
      return state.originalScrollIntoView.apply(this, args);
    };
    Object.defineProperty(guardedScrollIntoView, '__awPracticeGuard', { value: true });
    Element.prototype.scrollIntoView = guardedScrollIntoView;

    window.scrollTo = (...args) => {
      if (state.open) return undefined;
      return state.originalScrollTo(...args);
    };
    window.scrollBy = (...args) => {
      if (state.open) return undefined;
      return state.originalScrollBy(...args);
    };
  }

  function safeFocus(element) {
    if (!(element instanceof HTMLElement)) return;
    try {
      element.focus({ preventScroll: true });
    } catch {
      element.focus();
    }
  }

  function waitForPracticeRoot(attempts = 24) {
    return new Promise((resolve) => {
      const check = (remaining) => {
        const root = findPracticeRoot();
        if (root || remaining <= 0) {
          resolve(root);
          return;
        }
        requestAnimationFrame(() => check(remaining - 1));
      };
      check(attempts);
    });
  }

  async function resolvePracticeRoot() {
    let root = findPracticeRoot();
    if (root) return root;

    const trigger = findPracticeTrigger();
    if (trigger) {
      trigger.click();
      root = await waitForPracticeRoot();
    }
    return root;
  }

  async function openPractice() {
    if (state.open) return;
    createShell();
    state.returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : state.launcher;

    const root = await resolvePracticeRoot();
    if (!root) {
      state.translationEl.textContent = 'Practice content is not available on this screen.';
      state.explanationEl.textContent = 'Open the article trainer once, then use the Practice button again.';
      state.statusEl.textContent = 'Could not locate the article trainer.';
      return;
    }

    state.root = root;
    state.originalParent = root.parentNode;
    state.originalNextSibling = root.nextSibling;
    state.answered = 0;
    updateProgress();

    state.open = true;
    setViewportHeight();
    lockPage();
    installScrollGuards();

    root.classList.add(ROOT_CLASS);
    state.mount.replaceChildren(root);
    state.shell.hidden = false;
    state.launcher?.setAttribute('aria-expanded', 'true');

    markPracticeContent();
    observePractice();
    updateEnglishSupport();

    requestAnimationFrame(() => {
      markPracticeContent();
      const firstChoice = getArticleChoices(root, true)[0];
      safeFocus(firstChoice || state.shell.querySelector('.aw-practice-close'));
    });
  }

  function closePractice() {
    if (!state.open) return;
    state.observer?.disconnect();
    state.resizeObserver?.disconnect();
    state.translationAbort?.abort();
    cancelAnimationFrame(state.updateFrame);

    const root = state.root;
    if (root) {
      root.classList.remove(ROOT_CLASS);
      root.querySelectorAll('[data-aw-practice-prompt], [data-aw-practice-feedback], [data-aw-article-choice], [data-aw-article-choice-group]')
        .forEach((element) => {
          element.removeAttribute('data-aw-practice-prompt');
          element.removeAttribute('data-aw-practice-feedback');
          element.removeAttribute('data-aw-article-choice');
          element.removeAttribute('data-aw-article-choice-group');
        });

      if (state.originalParent?.isConnected) {
        if (state.originalNextSibling?.parentNode === state.originalParent) {
          state.originalParent.insertBefore(root, state.originalNextSibling);
        } else {
          state.originalParent.append(root);
        }
      }
    }

    state.shell.hidden = true;
    state.launcher?.setAttribute('aria-expanded', 'false');
    state.open = false;
    unlockPage();
    safeFocus(state.returnFocus || state.launcher);

    state.root = null;
    state.originalParent = null;
    state.originalNextSibling = null;
  }

  function choosePromptCandidate() {
    if (!state.root) return null;
    const selector = [
      '[data-question]', '[data-word]', '[data-noun]',
      '[class*="prompt" i]', '[class*="question" i]', '[class*="word" i]', '[class*="noun" i]',
      '[id*="prompt" i]', '[id*="question" i]', '[id*="word" i]', '[id*="noun" i]',
      'h1', 'h2', 'h3', 'h4', 'strong'
    ].join(',');

    const candidates = Array.from(state.root.querySelectorAll(selector))
      .filter((element) => !exactArticle(element))
      .filter((element) => !element.closest('[data-aw-practice-feedback]'))
      .map((element) => {
        const text = elementText(element);
        let score = 0;
        if (!text || text.length > 180) return { element, score: -Infinity };
        if (isVisible(element)) score += 30;
        if (element.matches('[data-word], [data-noun], [class*="word" i], [class*="noun" i], [id*="word" i], [id*="noun" i]')) score += 35;
        if (element.matches('h1, h2, h3, h4')) score += 15;
        if (/\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]{2,}\b/.test(text)) score += 20;
        const size = Number.parseFloat(getComputedStyle(element).fontSize) || 0;
        score += Math.min(20, size / 2);
        return { element, score };
      })
      .filter(({ score }) => Number.isFinite(score))
      .sort((a, b) => b.score - a.score);

    return candidates[0]?.element || null;
  }

  function feedbackCandidates() {
    if (!state.root) return [];
    const selector = [
      '[data-feedback]', '[data-definition]', '[data-meaning]', '[data-explanation]', '[data-result]',
      '[class*="feedback" i]', '[class*="definition" i]', '[class*="meaning" i]', '[class*="explanation" i]',
      '[class*="result" i]', '[class*="answer" i]', '[class*="hint" i]',
      '[id*="feedback" i]', '[id*="definition" i]', '[id*="meaning" i]', '[id*="explanation" i]',
      '[role="alert"]', '[aria-live]'
    ].join(',');

    return Array.from(state.root.querySelectorAll(selector))
      .filter((element) => element !== state.root)
      .filter((element) => normalize(element.textContent).length >= 3)
      .filter((element) => !element.closest('.aw-practice-support'))
      .sort((a, b) => Number(isVisible(b)) - Number(isVisible(a)));
  }

  function markPracticeContent() {
    if (!state.root) return;

    state.root.querySelectorAll('[data-aw-practice-prompt], [data-aw-practice-feedback], [data-aw-article-choice], [data-aw-article-choice-group]')
      .forEach((element) => {
        element.removeAttribute('data-aw-practice-prompt');
        element.removeAttribute('data-aw-practice-feedback');
        element.removeAttribute('data-aw-article-choice');
        element.removeAttribute('data-aw-article-choice-group');
      });

    const choices = getArticleChoices(state.root);
    choices.forEach((choice) => choice.setAttribute('data-aw-article-choice', normalizeKey(elementText(choice))));
    const group = commonAncestor(choices.slice(0, 3));
    group?.setAttribute('data-aw-article-choice-group', '');

    const prompt = choosePromptCandidate();
    prompt?.setAttribute('data-aw-practice-prompt', '');
    feedbackCandidates().slice(0, 4).forEach((element) => element.setAttribute('data-aw-practice-feedback', ''));
  }

  function observePractice() {
    state.observer?.disconnect();
    state.observer = new MutationObserver(() => {
      markPracticeContent();
      queueSupportUpdate();
    });
    state.observer.observe(state.root, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['class', 'hidden', 'aria-hidden', 'data-word', 'data-noun', 'data-definition', 'data-translation']
    });

    if ('ResizeObserver' in window) {
      state.resizeObserver = new ResizeObserver(setViewportHeight);
      state.resizeObserver.observe(document.documentElement);
    }
  }

  function queueSupportUpdate() {
    cancelAnimationFrame(state.updateFrame);
    state.updateFrame = requestAnimationFrame(updateEnglishSupport);
  }

  function updateProgress() {
    if (state.progressEl) state.progressEl.textContent = String(state.answered);
  }

  function extractGermanTerm() {
    if (!state.root) return '';

    const dataElements = [state.root, ...state.root.querySelectorAll('[data-word], [data-noun], [data-german], [data-de], [lang="de"]')];
    const dataKeys = ['word', 'noun', 'german', 'de', 'lemma', 'term'];
    for (const element of dataElements) {
      for (const key of dataKeys) {
        const value = normalize(element.dataset?.[key] || element.getAttribute?.(`data-${key}`));
        if (value && value.length <= 80) return cleanGermanTerm(value);
      }
    }

    const prompt = state.root.querySelector('[data-aw-practice-prompt]');
    const texts = [elementText(prompt), ...Array.from(state.root.querySelectorAll('h1, h2, h3, h4, strong, b')).map(elementText)];
    for (const text of texts) {
      const cleaned = cleanGermanTerm(text);
      if (cleaned) return cleaned;
    }
    return '';
  }

  function cleanGermanTerm(value) {
    const text = normalize(value)
      .replace(/^(der|die|das)\s+/i, '')
      .replace(/[_–—]+/g, ' ')
      .replace(/[?!.:;,]+$/g, '');
    if (!text || text.length > 100) return '';

    const candidates = text.match(/\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]{2,}\b/g) || [];
    const noun = candidates.find((candidate) => !IGNORED_PROMPT_WORDS.has(normalizeKey(candidate)));
    if (noun) return noun;

    if (/^[A-Za-zÄÖÜäöüß-]{2,40}$/.test(text) && !IGNORED_PROMPT_WORDS.has(normalizeKey(text))) return text;
    return '';
  }

  function extractGermanExplanation() {
    if (!state.root) return '';
    const values = feedbackCandidates()
      .map(elementText)
      .filter((text) => text.length >= 8 && text.length <= 650)
      .filter((text) => !ARTICLE_WORDS.has(normalizeKey(text)));
    return values[0] || '';
  }

  function readExplicitTranslation(term) {
    if (!state.root) return '';
    const selectors = [
      '[data-english]', '[data-en]', '[data-translation-en]', '[data-translation]',
      '[class*="english" i]', '[class*="translation" i]', '[class*="meaning" i]',
      '[id*="english" i]', '[id*="translation" i]'
    ].join(',');
    for (const element of state.root.querySelectorAll(selectors)) {
      const value = normalize(
        element.dataset?.english || element.dataset?.en || element.dataset?.translationEn ||
        element.dataset?.translation || element.textContent
      );
      if (!value || value === term || value.length > 220 || /^der|die|das$/i.test(value)) continue;
      if (/[A-Za-z]/.test(value)) return value;
    }
    return '';
  }

  function loadCache() {
    if (state.cache) return state.cache;
    try {
      const parsed = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
      state.cache = parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      state.cache = {};
    }
    return state.cache;
  }

  function saveCachedTranslation(source, translated) {
    if (!source || !translated) return;
    const cache = loadCache();
    cache[normalizeKey(source)] = translated;
    const entries = Object.entries(cache).slice(-500);
    state.cache = Object.fromEntries(entries);
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(state.cache));
    } catch {
      // Storage may be unavailable in private browsing; the session still works.
    }
  }

  function cachedTranslation(source) {
    return loadCache()[normalizeKey(source)] || '';
  }

  function buildTranslationIndex() {
    if (state.translationIndex) return state.translationIndex;
    const index = new Map();
    const seen = new WeakSet();
    let visited = 0;
    const maxVisited = 30000;
    const germanKeys = ['german', 'de', 'word', 'noun', 'lemma', 'term', 'wort', 'nomen', 'name', 'prompt'];
    const englishKeys = ['english', 'en', 'translation', 'meaning', 'gloss', 'definitionen', 'definition_en', 'translationen', 'translation_en'];

    const add = (german, english) => {
      const de = normalize(german);
      const en = normalize(english);
      if (!de || !en || de.length > 100 || en.length > 280 || de === en) return;
      index.set(normalizeKey(cleanGermanTerm(de) || de), en);
    };

    const visit = (value, depth = 0, mapKey = '') => {
      if (visited >= maxVisited || depth > 7 || value == null) return;
      if (typeof value === 'string') {
        if (mapKey && /^[A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]{1,60}$/.test(mapKey)) add(mapKey, value);
        return;
      }
      if (typeof value !== 'object') return;
      if (seen.has(value)) return;
      seen.add(value);
      visited += 1;

      if (Array.isArray(value)) {
        value.slice(0, 12000).forEach((entry) => visit(entry, depth + 1));
        return;
      }

      const keys = Object.keys(value);
      const lowerToActual = new Map(keys.map((key) => [normalizeKey(key).replace(/[^a-z_]/g, ''), key]));
      const germanKey = germanKeys.map((key) => lowerToActual.get(key)).find(Boolean);
      const englishKey = englishKeys.map((key) => lowerToActual.get(key)).find(Boolean);
      if (germanKey && englishKey) add(value[germanKey], value[englishKey]);

      for (const [key, child] of Object.entries(value).slice(0, 15000)) {
        if (typeof child === 'string' && /^[A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]{1,60}$/.test(key)) add(key, child);
        else visit(child, depth + 1, key);
      }
    };

    const globalCandidates = Object.getOwnPropertyNames(window)
      .filter((key) => /vocab|word|noun|lexicon|dictionary|artikel|data|items|terms/i.test(key))
      .slice(0, 120);
    for (const key of globalCandidates) {
      try {
        visit(window[key], 0, key);
      } catch {
        // Some host objects throw when read; skip them.
      }
    }

    try {
      for (let i = 0; i < localStorage.length; i += 1) {
        const key = localStorage.key(i);
        if (!key) continue;
        const raw = localStorage.getItem(key);
        if (!raw || raw.length > 8_000_000 || !/^[\[{]/.test(raw.trim())) continue;
        try { visit(JSON.parse(raw), 0, key); } catch { /* not JSON */ }
      }
    } catch {
      // localStorage may be blocked.
    }

    state.translationIndex = index;
    return index;
  }

  function localTranslation(term) {
    if (!term) return '';
    const explicit = readExplicitTranslation(term);
    if (explicit) return explicit;
    const cached = cachedTranslation(term);
    if (cached) return cached;
    const index = buildTranslationIndex();
    return index.get(normalizeKey(term)) || '';
  }

  async function translateGerman(text, signal) {
    const source = normalize(text).slice(0, 480);
    if (!source) return '';
    const cached = cachedTranslation(source);
    if (cached) return cached;

    const url = new URL('https://api.mymemory.translated.net/get');
    url.searchParams.set('q', source);
    url.searchParams.set('langpair', 'de|en');
    const response = await fetch(url, {
      method: 'GET',
      mode: 'cors',
      credentials: 'omit',
      cache: 'force-cache',
      signal
    });
    if (!response.ok) throw new Error(`Translation request failed: ${response.status}`);
    const payload = await response.json();
    const translated = normalize(payload?.responseData?.translatedText);
    if (!translated || translated === source || /QUERY LENGTH LIMIT EXCEEDED/i.test(translated)) return '';
    saveCachedTranslation(source, translated);
    return translated;
  }

  function setSupport(translation, explanation, status = '') {
    state.translationEl.textContent = translation || 'English translation unavailable.';
    state.explanationEl.textContent = explanation || 'Choose an article to reveal feedback and its English explanation.';
    state.statusEl.textContent = status;
  }

  async function updateEnglishSupport() {
    if (!state.open || !state.root) return;
    const sequence = ++state.translationSequence;
    state.translationAbort?.abort();
    state.translationAbort = new AbortController();
    const signal = state.translationAbort.signal;

    const term = extractGermanTerm();
    const germanExplanation = extractGermanExplanation();
    if (!term && !germanExplanation) {
      setSupport('Choose an answer to see the English meaning.', 'Definitions and feedback will stay inside this fixed screen.');
      return;
    }

    const local = localTranslation(term);
    state.translationEl.textContent = local || (term ? 'Translating…' : 'English meaning will appear here.');
    state.explanationEl.textContent = germanExplanation ? 'Translating explanation…' : 'Choose an article to reveal the explanation.';

    let translatedTerm = local;
    let translatedExplanation = '';
    try {
      const requests = [];
      if (!translatedTerm && term) requests.push(translateGerman(term, signal).then((value) => { translatedTerm = value; }));
      if (germanExplanation && germanExplanation !== term) {
        requests.push(translateGerman(germanExplanation, signal).then((value) => { translatedExplanation = value; }));
      }
      await Promise.all(requests);
    } catch (error) {
      if (error?.name === 'AbortError') return;
    }

    if (!state.open || sequence !== state.translationSequence) return;
    const termFallback = term ? `${term} — English translation unavailable offline.` : 'English translation unavailable offline.';
    const explanationFallback = germanExplanation
      ? 'The German explanation is shown in the exercise; its English translation is unavailable offline.'
      : 'Choose an article to reveal the explanation.';
    setSupport(translatedTerm || termFallback, translatedExplanation || explanationFallback, translatedTerm ? `English meaning for ${term}.` : 'English translation could not be loaded.');
  }

  function focusableElements() {
    if (!state.shell) return [];
    return Array.from(state.shell.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
      .filter(isVisible);
  }

  function handleKeydown(event) {
    if (!state.open) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closePractice();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = focusableElements();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      safeFocus(last);
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      safeFocus(first);
    }
  }

  function handleExistingPracticeTrigger(event) {
    if (state.open) return;
    const trigger = event.target.closest('button, a, [role="button"], [role="tab"], input[type="button"], input[type="submit"]');
    if (!trigger || trigger.id === LAUNCH_ID || trigger.closest(`#${SHELL_ID}`) || triggerScore(trigger) <= 0) return;

    const root = findPracticeRoot();
    if (root) {
      event.preventDefault();
      event.stopPropagation();
      openPractice();
    } else {
      setTimeout(() => openPractice(), 0);
    }
  }

  function initialize() {
    if (!document.body) return;
    createShell();
    createLauncher();
    installScrollGuards();
    setViewportHeight();

    document.addEventListener('keydown', handleKeydown, true);
    document.addEventListener('click', handleExistingPracticeTrigger, true);
    window.addEventListener('resize', setViewportHeight, { passive: true });
    window.visualViewport?.addEventListener('resize', setViewportHeight, { passive: true });

    const launcherObserver = new MutationObserver(() => {
      if (!document.getElementById(LAUNCH_ID)) createLauncher();
    });
    launcherObserver.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
