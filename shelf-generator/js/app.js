'use strict';

const PRODUCTS = [
  { id: 'water', name: 'Agua mineral', price: 2.50, symbol: 'product-water' },
  { id: 'milk', name: 'Leche entera', price: 4.80, symbol: 'product-milk' },
  { id: 'soda', name: 'Gaseosa', price: 3.50, symbol: 'product-soda' },
  { id: 'juice', name: 'Jugo de naranja', price: 4.20, symbol: 'product-juice' },
  { id: 'cookies', name: 'Galletas', price: 3.00, symbol: 'product-cookies' },
  { id: 'cereal', name: 'Cereal', price: 9.90, symbol: 'product-cereal' },
  { id: 'canned', name: 'Conserva', price: 5.60, symbol: 'product-canned' },
  { id: 'detergent', name: 'Detergente', price: 8.50, symbol: 'product-detergent' }
];

const ROWS = 4;
const COLUMNS = 8;
const TOTAL_SLOTS = ROWS * COLUMNS;
const state = {
  slots: Array.from({ length: TOTAL_SLOTS }, (_, index) => index % 9 === 0 ? null : PRODUCTS[(index * 3 + Math.floor(index / COLUMNS)) % PRODUCTS.length].id),
  selectedSlot: null,
  captureMode: false
};

const elements = {
  grid: document.getElementById('shelfGrid'),
  select: document.getElementById('productSelect'),
  apply: document.getElementById('applyButton'),
  empty: document.getElementById('emptyButton'),
  random: document.getElementById('randomButton'),
  clear: document.getElementById('clearButton'),
  presentation: document.getElementById('presentationButton'),
  slotNumber: document.getElementById('selectedSlotNumber'),
  slotText: document.getElementById('selectedSlotText'),
  occupied: document.getElementById('occupiedCount'),
  emptyCount: document.getElementById('emptyCount'),
  summary: document.getElementById('summaryList'),
  state: document.getElementById('shelfState'),
  hint: document.getElementById('shelfHint')
};

function productById(id) {
  return PRODUCTS.find(product => product.id === id) || null;
}

function money(value) {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value);
}

function renderProduct(product) {
  const wrapper = document.createElement('div');
  wrapper.className = 'product-content';

  const art = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  art.setAttribute('class', 'product-art');
  art.setAttribute('viewBox', '0 0 100 100');
  art.setAttribute('role', 'img');
  art.setAttribute('aria-label', product.name);
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  use.setAttribute('href', `assets/products.svg#${product.symbol}`);
  art.appendChild(use);

  const name = document.createElement('span');
  name.className = 'product-name';
  name.textContent = product.name;
  const price = document.createElement('span');
  price.className = 'product-price';
  price.textContent = money(product.price);
  wrapper.append(art, name, price);
  return wrapper;
}

function renderShelf() {
  elements.grid.replaceChildren();
  state.slots.forEach((productId, index) => {
    const product = productById(productId);
    const slot = document.createElement('button');
    slot.type = 'button';
    slot.className = `shelf-slot${product ? '' : ' empty'}${state.selectedSlot === index ? ' selected' : ''}`;
    slot.setAttribute('aria-label', product ? `Espacio ${index + 1}: ${product.name}` : `Espacio ${index + 1}: vacío`);
    slot.setAttribute('aria-pressed', String(state.selectedSlot === index));
    const number = document.createElement('span');
    number.className = 'slot-index';
    number.textContent = String(index + 1).padStart(2, '0');
    slot.appendChild(number);
    if (product) {
      slot.appendChild(renderProduct(product));
    } else {
      const empty = document.createElement('span');
      empty.className = 'empty-mark';
      empty.textContent = '＋';
      empty.setAttribute('aria-hidden', 'true');
      const label = document.createElement('span');
      label.className = 'product-name';
      label.textContent = 'Espacio libre';
      slot.append(empty, label);
    }
    slot.addEventListener('click', () => selectSlot(index));
    elements.grid.appendChild(slot);
  });
  renderSummary();
}

function renderSummary() {
  const counts = new Map(PRODUCTS.map(product => [product.id, 0]));
  state.slots.forEach(id => { if (id && counts.has(id)) counts.set(id, counts.get(id) + 1); });
  const occupied = state.slots.filter(Boolean).length;
  elements.occupied.textContent = String(occupied);
  elements.emptyCount.textContent = String(TOTAL_SLOTS - occupied);
  elements.summary.replaceChildren();
  const used = PRODUCTS.filter(product => counts.get(product.id) > 0);
  if (used.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'summary-empty';
    empty.textContent = 'Todavía no hay productos en exhibición.';
    elements.summary.appendChild(empty);
    return;
  }
  used.forEach(product => {
    const row = document.createElement('div');
    row.className = 'summary-row';
    const name = document.createElement('span');
    name.textContent = product.name;
    const count = document.createElement('strong');
    count.textContent = `${counts.get(product.id)} espacio(s)`;
    row.append(name, count);
    elements.summary.appendChild(row);
  });
}

function selectSlot(index) {
  state.selectedSlot = index;
  const current = productById(state.slots[index]);
  elements.slotNumber.textContent = `#${String(index + 1).padStart(2, '0')}`;
  elements.slotText.textContent = current ? `Producto actual: ${current.name}. Puedes reemplazarlo o dejar el espacio vacío.` : 'Este espacio está vacío. Selecciona un producto para colocarlo.';
  elements.select.disabled = false;
  elements.select.replaceChildren();
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccionar producto…';
  elements.select.appendChild(placeholder);
  PRODUCTS.forEach(product => {
    const option = document.createElement('option');
    option.value = product.id;
    option.textContent = `${product.name} · ${money(product.price)}`;
    elements.select.appendChild(option);
  });
  elements.select.value = state.slots[index] || '';
  elements.apply.disabled = false;
  elements.empty.disabled = !state.slots[index];
  renderShelf();
}

function applySelection() {
  if (state.selectedSlot === null) return;
  const productId = elements.select.value;
  if (!productById(productId)) {
    elements.slotText.textContent = 'Selecciona un producto válido.';
    return;
  }
  state.slots[state.selectedSlot] = productId;
  elements.state.textContent = 'Escenario modificado';
  selectSlot(state.selectedSlot);
}

function emptySelectedSlot() {
  if (state.selectedSlot === null) return;
  state.slots[state.selectedSlot] = null;
  elements.state.textContent = 'Escenario modificado';
  selectSlot(state.selectedSlot);
}

function generateDistribution() {
  state.slots = Array.from({ length: TOTAL_SLOTS }, () => Math.random() < 0.16 ? null : PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)].id);
  state.selectedSlot = null;
  resetEditor();
  elements.state.textContent = 'Nueva distribución';
  renderShelf();
}

function clearShelf() {
  state.slots = Array(TOTAL_SLOTS).fill(null);
  state.selectedSlot = null;
  resetEditor();
  elements.state.textContent = 'Anaquel vacío';
  renderShelf();
}

function resetEditor() {
  elements.slotNumber.textContent = '—';
  elements.slotText.textContent = 'Selecciona cualquiera de los 32 espacios del anaquel.';
  elements.select.disabled = true;
  elements.select.replaceChildren();
  const option = document.createElement('option');
  option.value = '';
  option.textContent = 'Selecciona un espacio primero';
  elements.select.appendChild(option);
  elements.apply.disabled = true;
  elements.empty.disabled = true;
}

function toggleCaptureMode() {
  state.captureMode = !state.captureMode;
  document.body.classList.toggle('capture-mode', state.captureMode);
  elements.presentation.textContent = state.captureMode ? '✕ Salir de captura' : '▣ Modo captura';
  elements.hint.textContent = state.captureMode ? 'Vista preparada para fotografiar el anaquel. Pulsa “Salir de captura” para editar.' : 'Selecciona un espacio para asignar o retirar un producto.';
  if (state.captureMode) {
    state.selectedSlot = null;
    resetEditor();
    renderShelf();
  }
}

elements.apply.addEventListener('click', applySelection);
elements.empty.addEventListener('click', emptySelectedSlot);
elements.random.addEventListener('click', generateDistribution);
elements.clear.addEventListener('click', clearShelf);
elements.presentation.addEventListener('click', toggleCaptureMode);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && state.captureMode) toggleCaptureMode();
});
renderShelf();
