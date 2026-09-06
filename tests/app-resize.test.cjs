const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = readFileSync(join(__dirname, '..', 'app.js'), 'utf8');

async function createViewer(initialWidth = 595, initialHash = '') {
  let width = initialWidth;
  let inObserver = false;
  let observer;
  let frameId = 0;
  const frames = new Map();
  const writes = [];
  const classes = new Set();
  function target(properties = {}) {
    const listeners = new Map();
    return {
      addEventListener(type, callback) { listeners.set(type, callback); },
      emit(type, event = {}) { listeners.get(type)?.({ target: this, ...event }); },
      closest() { return null; },
      ...properties,
    };
  }
  function style() {
    return new Proxy({}, {
      set(object, property, value) {
        assert.equal(inObserver, false, 'layout writes must not occur during observer delivery');
        writes.push([property, value]);
        object[property] = value;
        return true;
      },
    });
  }
  const pages = Array.from({ length: 13 }, (_, index) => {
    const paper = { style: style() };
    return { dataset: { preview: String(index + 1) }, style: style(), paper,
      querySelector() { return paper; } };
  });
  const notes = pages.map(page => ({ dataset: { notesFor: page.dataset.preview } }));
  const controls = Object.fromEntries(['page', 'previous', 'next', 'counter', 'guides']
    .map(name => [name, target({ closest() { return this; } })]));
  const root = {
    isConnected: true,
    querySelectorAll(selector) { return selector.startsWith('.page-preview') ? pages : notes; },
    querySelector(selector) { return controls[selector.replace('#simpaisa-v26-', '')]; },
    classList: { toggle(name, enabled) { enabled ? classes.add(name) : classes.delete(name); } },
  };
  const window = target();
  let hash = initialHash;
  const location = {
    get hash() { return hash; },
    set hash(value) { hash = value.startsWith('#') ? value : `#${value}`; },
  };
  vm.runInNewContext(source, {
    document: { getElementById: () => root, fonts: { ready: Promise.resolve() } },
    window, location,
    getComputedStyle: () => ({ width: `${width}px` }),
    requestAnimationFrame(callback) { const id = frameId++; frames.set(id, callback); return id; },
    ResizeObserver: class {
      constructor(callback) { observer = callback; }
      observe(element) { assert.equal(element, root); }
    },
  });
  await Promise.resolve();
  return {
    root, pages, notes, controls, classes, frames, writes, window, location,
    notify(nextWidth) {
      width = nextWidth;
      inObserver = true;
      try { observer([{ target: root, contentRect: { width, height: 900 } }]); }
      finally { inObserver = false; }
    },
    flushFrame() {
      const callbacks = [...frames.values()];
      frames.clear();
      callbacks.forEach(callback => callback());
    },
    navigate(nextHash) { location.hash = nextHash; window.emit('hashchange'); },
  };
}

test('coalesces width changes and settles repeated observer feedback without layout writes', async () => {
  const viewer = await createViewer();
  assert.equal(viewer.frames.size, 1);
  assert.equal(viewer.writes.length, 0);
  viewer.flushFrame();
  assert.equal(viewer.writes.length, 26);
  viewer.notify(400);
  viewer.notify(360);
  viewer.notify(360);
  assert.equal(viewer.frames.size, 1);
  assert.equal(viewer.writes.length, 26);
  viewer.flushFrame();
  for (const page of viewer.pages) {
    assert.equal(page.paper.style.transform, `scale(${360 / 595})`);
    assert.ok(Math.abs(Number.parseFloat(page.style.height) - 842 * 360 / 595) < 1e-8);
  }
  const writesAfterResize = viewer.writes.length;
  for (let cycle = 0; cycle < 10; cycle++) {
    viewer.notify(360);
    viewer.flushFrame();
  }
  assert.equal(viewer.frames.size, 0);
  assert.equal(viewer.writes.length, writesAfterResize);
});

test('ignores zero and non-finite widths, retaining usable sizes through hiding and reopening', async () => {
  const viewer = await createViewer(0);
  assert.equal(viewer.frames.size, 0);
  for (const width of [0, -1, NaN, Infinity]) viewer.notify(width);
  assert.equal(viewer.frames.size, 0);
  viewer.notify(595);
  viewer.flushFrame();
  assert.equal(viewer.pages[0].style.height, '842px');
  const initialWrites = viewer.writes.length;
  viewer.notify(0);
  viewer.notify(595);
  viewer.flushFrame();
  assert.equal(viewer.writes.length, initialWrites);
  viewer.notify(400);
  viewer.notify(595);
  viewer.flushFrame();
  assert.equal(viewer.writes.length, initialWrites, 'a resize that returns to the applied width needs no writes');
});

test('does not size a detached viewer and retries when navigation makes it available again', async () => {
  const viewer = await createViewer();
  viewer.root.isConnected = false;
  viewer.flushFrame();
  assert.equal(viewer.writes.length, 0);
  viewer.root.isConnected = true;
  viewer.navigate('#page-2');
  viewer.flushFrame();
  assert.equal(viewer.pages[1].style.height, '842px');
});

test('preserves hash, selector, buttons, keyboard, notes and guides at an unchanged width', async () => {
  const viewer = await createViewer(595, '#page-5');
  viewer.flushFrame();
  const initialWrites = viewer.writes.length;
  assert.equal(viewer.controls.page.value, '5');
  assert.equal(viewer.controls.counter.textContent, '5 / 13');
  assert.equal(viewer.pages[4].hidden, false);
  assert.equal(viewer.notes[4].hidden, false);
  viewer.controls.page.value = '13';
  viewer.controls.page.emit('change');
  assert.equal(viewer.location.hash, '#page-13');
  viewer.window.emit('hashchange');
  assert.equal(viewer.controls.next.disabled, true);
  viewer.controls.previous.emit('click');
  viewer.window.emit('hashchange');
  assert.equal(viewer.controls.page.value, '12');
  viewer.navigate('#page-999');
  assert.equal(viewer.controls.page.value, '1');
  assert.equal(viewer.controls.previous.disabled, true);
  viewer.controls.next.emit('click');
  viewer.window.emit('hashchange');
  assert.equal(viewer.controls.page.value, '2');
  viewer.window.emit('keydown', { key: 'ArrowRight', target: { closest: () => null } });
  viewer.window.emit('hashchange');
  assert.equal(viewer.controls.page.value, '3');
  viewer.window.emit('keydown', { key: 'ArrowRight', target: viewer.controls.page });
  assert.equal(viewer.location.hash, '#page-3');
  viewer.controls.guides.checked = true;
  viewer.controls.guides.emit('change');
  assert.equal(viewer.classes.has('show-guides'), true);
  viewer.controls.guides.checked = false;
  viewer.controls.guides.emit('change');
  assert.equal(viewer.classes.has('show-guides'), false);
  assert.equal(viewer.frames.size, 0);
  assert.equal(viewer.writes.length, initialWrites);
  assert.deepEqual(viewer.pages.filter(page => !page.hidden).map(page => page.dataset.preview), ['3']);
  assert.deepEqual(viewer.notes.filter(note => !note.hidden).map(note => note.dataset.notesFor), ['3']);
});
