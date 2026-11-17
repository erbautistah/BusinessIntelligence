'use strict';

const PRODUCTS = [
  { id: 'water', sku: 'BEB-001', name: 'Agua mineral', category: 'Bebidas', price: 2.50, symbol: 'product-water' },
  { id: 'milk', sku: 'LAC-001', name: 'Leche entera', category: 'Lácteos', price: 4.80, symbol: 'product-milk' },
  { id: 'soda', sku: 'BEB-002', name: 'Gaseosa', category: 'Bebidas', price: 3.50, symbol: 'product-soda' },
  { id: 'juice', sku: 'BEB-003', name: 'Jugo de naranja', category: 'Bebidas', price: 4.20, symbol: 'product-juice' },
  { id: 'cookies', sku: 'SNK-001', name: 'Galletas', category: 'Snacks', price: 3.00, symbol: 'product-cookies' },
  { id: 'cereal', sku: 'DES-001', name: 'Cereal', category: 'Desayunos', price: 9.90, symbol: 'product-cereal' },
  { id: 'canned', sku: 'ABR-001', name: 'Conserva', category: 'Abarrotes', price: 5.60, symbol: 'product-canned' },
  { id: 'detergent', sku: 'LIM-001', name: 'Detergente', category: 'Limpieza', price: 8.50, symbol: 'product-detergent' }
];

const ROWS = 4;
const COLUMNS = 8;
const TOTAL_SLOTS = ROWS * COLUMNS;
const SCENARIOS = {
  equilibrado: {
    name: 'Exhibición equilibrada',
    counts: { water: 4, milk: 4, soda: 4, juice: 4, cookies: 3, cereal: 3, canned: 3, detergent: 3 }
  },
  faltantes: {
    name: 'Faltantes de productos',
    counts: { water: 3, milk: 4, soda: 0, juice: 2, cookies: 3, cereal: 3, canned: 3, detergent: 0 }
  },
  completo: {
    name: 'Anaquel completo',
    counts: { water: 4, milk: 4, soda: 4, juice: 4, cookies: 4, cereal: 4, canned: 4, detergent: 4 }
  },
  bebidas: {
    name: 'Predominio de bebidas',
    counts: { water: 7, milk: 1, soda: 7, juice: 5, cookies: 1, cereal: 1, canned: 1, detergent: 1 }
  }
};

const state = {
  slots: [],
  selectedSlot: null,
  captureMode: false,
  scenarioId: 'equilibrado',
  scenarioName: SCENARIOS.equilibrado.name
};

const elements = {
  grid: document.getElementById('shelfGrid'),
  select: document.getElementById('productSelect'),
  apply: document.getElementById('applyButton'),
  empty: document.getElementById('emptyButton'),
  random: document.getElementById('randomButton'),
  clear: document.getElementById('clearButton'),
  scenarioSelect: document.getElementById('scenarioSelect'),
  scenarioButton: document.getElementById('scenarioButton'),
  presentation: document.getElementById('presentationButton'),
  captureExit: document.getElementById('captureExitButton'),
  slotNumber: document.getElementById('selectedSlotNumber'),
  slotText: document.getElementById('selectedSlotText'),
  occupied: document.getElementById('occupiedCount'),
  emptyCount: document.getElementById('emptyCount'),
  variety: document.getElementById('varietyCount'),
  fillRate: document.getElementById('fillRate'),
  displayValue: document.getElementById('displayValue'),
  summary: document.getElementById('summaryList'),
  shelfState: document.getElementById('shelfState'),
  hint: document.getElementById('shelfHint'),
  png: document.getElementById('pngButton'),
  json: document.getElementById('jsonButton'),
  csv: document.getElementById('csvButton'),
  exportStatus: document.getElementById('exportStatus')
};

function productById(id) {
  return PRODUCTS.find(product => product.id === id) || null;
}

function money(value) {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value);
}

function shuffle(items) {
  const result = items.slice();
  for (let index = result.length - 1; index > 0; index -= 1) {
    const target = Math.floor(Math.random() * (index + 1));
    const temp = result[index];
    result[index] = result[target];
    result[target] = temp;
  }
  return result;
}

function slotsFromCounts(counts) {
  const values = [];
  PRODUCTS.forEach(product => {
    const amount = Math.max(0, Math.min(TOTAL_SLOTS, Number(counts[product.id]) || 0));
    for (let index = 0; index < amount; index += 1) values.push(product.id);
  });
  while (values.length < TOTAL_SLOTS) values.push(null);
  return shuffle(values.slice(0, TOTAL_SLOTS));
}

function applyScenario(scenarioId) {
  const scenario = SCENARIOS[scenarioId];
  if (!scenario) return;
  state.slots = slotsFromCounts(scenario.counts);
  state.scenarioId = scenarioId;
  state.scenarioName = scenario.name;
  state.selectedSlot = null;
  resetEditor();
  elements.shelfState.textContent = scenario.name;
  renderShelf();
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
  use.setAttribute('href', 'assets/products.svg#' + product.symbol);
  art.appendChild(use);

  const info = document.createElement('div');
  info.className = 'product-info';

  const name = document.createElement('span');
  name.className = 'product-name';
  name.textContent = product.name;

  const price = document.createElement('span');
  price.className = 'product-price';
  price.textContent = money(product.price);

  info.append(name, price);
  wrapper.append(art, info);
  return wrapper;
}

function renderShelf() {
  elements.grid.replaceChildren();
  state.slots.forEach((productId, index) => {
    const product = productById(productId);
    const slot = document.createElement('button');
    slot.type = 'button';
    slot.className = 'shelf-slot' + (product ? '' : ' empty') + (state.selectedSlot === index ? ' selected' : '');
    slot.setAttribute('aria-label', product ? 'Espacio ' + (index + 1) + ': ' + product.name : 'Espacio ' + (index + 1) + ': vacío');
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
      empty.textContent = '+';
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

function getSummary() {
  const counts = {};
  PRODUCTS.forEach(product => { counts[product.id] = 0; });
  let occupied = 0;
  let displayValue = 0;
  state.slots.forEach(id => {
    const product = productById(id);
    if (!product) return;
    occupied += 1;
    counts[id] += 1;
    displayValue += product.price;
  });
  const productsUsed = PRODUCTS.filter(product => counts[product.id] > 0);
  return {
    occupied: occupied,
    empty: TOTAL_SLOTS - occupied,
    variety: productsUsed.length,
    fillRate: occupied / TOTAL_SLOTS,
    displayValue: Number(displayValue.toFixed(2)),
    counts: counts
  };
}

function renderSummary() {
  const summary = getSummary();
  elements.occupied.textContent = String(summary.occupied);
  elements.emptyCount.textContent = String(summary.empty);
  elements.variety.textContent = String(summary.variety);
  elements.fillRate.textContent = Math.round(summary.fillRate * 100) + '%';
  elements.displayValue.textContent = money(summary.displayValue);
  elements.summary.replaceChildren();

  const used = PRODUCTS.filter(product => summary.counts[product.id] > 0);
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
    count.textContent = summary.counts[product.id] + ' espacio(s)';
    row.append(name, count);
    elements.summary.appendChild(row);
  });
}

function selectSlot(index) {
  state.selectedSlot = index;
  const current = productById(state.slots[index]);
  elements.slotNumber.textContent = '#' + String(index + 1).padStart(2, '0');
  elements.slotText.textContent = current ? 'Producto actual: ' + current.name + '. Puedes reemplazarlo o dejar el espacio vacío.' : 'Este espacio está vacío. Selecciona un producto para colocarlo.';
  elements.select.disabled = false;
  elements.select.replaceChildren();

  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccionar producto…';
  elements.select.appendChild(placeholder);

  PRODUCTS.forEach(product => {
    const option = document.createElement('option');
    option.value = product.id;
    option.textContent = product.name + ' · ' + money(product.price);
    elements.select.appendChild(option);
  });

  elements.select.value = state.slots[index] || '';
  elements.apply.disabled = false;
  elements.empty.disabled = !state.slots[index];
  renderShelf();
}

function markAsCustom() {
  state.scenarioId = 'personalizado';
  state.scenarioName = 'Escenario personalizado';
  elements.shelfState.textContent = state.scenarioName;
}

function applySelection() {
  if (state.selectedSlot === null) return;
  const productId = elements.select.value;
  if (!productById(productId)) {
    elements.slotText.textContent = 'Selecciona un producto válido.';
    return;
  }
  state.slots[state.selectedSlot] = productId;
  markAsCustom();
  selectSlot(state.selectedSlot);
}

function emptySelectedSlot() {
  if (state.selectedSlot === null) return;
  state.slots[state.selectedSlot] = null;
  markAsCustom();
  selectSlot(state.selectedSlot);
}

function randomDistribution() {
  const occupancy = 0.55 + Math.random() * 0.36;
  const occupied = Math.round(TOTAL_SLOTS * occupancy);
  const values = [];
  for (let index = 0; index < occupied; index += 1) {
    values.push(PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)].id);
  }
  while (values.length < TOTAL_SLOTS) values.push(null);
  state.slots = shuffle(values);
  state.scenarioId = 'aleatorio';
  state.scenarioName = 'Distribución aleatoria';
  state.selectedSlot = null;
  resetEditor();
  elements.shelfState.textContent = state.scenarioName;
  renderShelf();
}

function clearShelf() {
  state.slots = Array(TOTAL_SLOTS).fill(null);
  state.scenarioId = 'vacio';
  state.scenarioName = 'Anaquel vacío';
  state.selectedSlot = null;
  resetEditor();
  elements.shelfState.textContent = state.scenarioName;
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
  elements.hint.textContent = state.captureMode ? 'Vista limpia para fotografiar. Pulsa “Salir de captura” o usa Escape para volver.' : 'Selecciona un espacio para asignar o retirar un producto. Los índices identifican cada posición.';
  if (state.captureMode) {
    state.selectedSlot = null;
    resetEditor();
    renderShelf();
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function fileBaseName() {
  const date = new Date().toISOString().replace(/[:.]/g, '-');
  return 'anaquel-' + state.scenarioId + '-' + date;
}

function buildExportData() {
  const summary = getSummary();
  return {
    schema_version: '1.0',
    exported_at: new Date().toISOString(),
    scenario: { id: state.scenarioId, name: state.scenarioName },
    shelf: { rows: ROWS, columns: COLUMNS, total_slots: TOTAL_SLOTS },
    assumptions: [
      'Cada espacio representa una posición de exhibición.',
      'Un espacio ocupado se contabiliza como una unidad visible para el cálculo referencial.',
      'Los precios son ilustrativos.',
      'La exhibición no equivale al stock total de almacén.'
    ],
    products: PRODUCTS.map(product => ({
      id: product.id,
      sku: product.sku,
      name: product.name,
      category: product.category,
      unit_price_pen: product.price
    })),
    slots: state.slots.map((id, index) => {
      const product = productById(id);
      return {
        slot: index + 1,
        row: Math.floor(index / COLUMNS) + 1,
        column: (index % COLUMNS) + 1,
        occupied: Boolean(product),
        product_id: product ? product.id : null,
        sku: product ? product.sku : null,
        product_name: product ? product.name : null,
        category: product ? product.category : null,
        unit_price_pen: product ? product.price : null
      };
    }),
    summary: {
      occupied_slots: summary.occupied,
      empty_slots: summary.empty,
      distinct_products: summary.variety,
      occupancy_rate: Number(summary.fillRate.toFixed(4)),
      estimated_display_value_pen: summary.displayValue,
      facings_by_product: summary.counts
    }
  };
}

function exportJson() {
  const data = buildExportData();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
  downloadBlob(blob, fileBaseName() + '.json');
  setExportStatus('JSON descargado.');
}

function csvCell(value) {
  if (value === null || value === undefined) return '';
  const text = String(value);
  return '"' + text.replace(/"/g, '""') + '"';
}

function exportCsv() {
  const rows = [['slot', 'row', 'column', 'occupied', 'product_id', 'sku', 'product_name', 'category', 'unit_price_pen']];
  buildExportData().slots.forEach(slot => {
    rows.push([slot.slot, slot.row, slot.column, slot.occupied, slot.product_id, slot.sku, slot.product_name, slot.category, slot.unit_price_pen]);
  });
  const csv = '\uFEFF' + rows.map(row => row.map(csvCell).join(';')).join('\r\n');
  downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8' }), fileBaseName() + '.csv');
  setExportStatus('CSV descargado.');
}

function svgElement(name, attributes, textContent) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.keys(attributes || {}).forEach(key => element.setAttribute(key, String(attributes[key])));
  if (textContent !== undefined) element.textContent = String(textContent);
  return element;
}

async function exportPng() {
  elements.png.disabled = true;
  setExportStatus('Preparando imagen PNG…');
  try {
    const response = await fetch('assets/products.svg');
    if (!response.ok) throw new Error('No se pudo cargar el catálogo SVG.');
    const spriteText = await response.text();
    const spriteDoc = new DOMParser().parseFromString(spriteText, 'image/svg+xml');
    if (spriteDoc.querySelector('parsererror')) throw new Error('El catálogo SVG no se pudo interpretar.');

    const width = 1600;
    const height = 1080;
    const svg = svgElement('svg', { xmlns: 'http://www.w3.org/2000/svg', width: width, height: height, viewBox: '0 0 1600 1080' });
    const defs = svgElement('defs');
    Array.from(spriteDoc.querySelectorAll('symbol')).forEach(symbol => defs.appendChild(symbol.cloneNode(true)));
    svg.appendChild(defs);

    svg.appendChild(svgElement('rect', { x: 0, y: 0, width: width, height: height, fill: '#f3f6f3' }));
    svg.appendChild(svgElement('text', { x: 72, y: 47, fill: '#60746a', 'font-family': 'Arial,sans-serif', 'font-size': 16, 'font-weight': 700, 'letter-spacing': 3 }, 'TIENDA INTELIGENTE · UNIDAD 4'));
    svg.appendChild(svgElement('text', { x: 72, y: 88, fill: '#1c2925', 'font-family': 'Arial,sans-serif', 'font-size': 34, 'font-weight': 700 }, 'Anaquel de supermercado'));
    svg.appendChild(svgElement('text', { x: 1528, y: 82, fill: '#1e5a48', 'font-family': 'Arial,sans-serif', 'font-size': 19, 'font-weight': 700, 'text-anchor': 'end' }, state.scenarioName));

    svg.appendChild(svgElement('rect', { x: 48, y: 112, width: 1504, height: 900, rx: 16, fill: '#9a6c3d' }));
    svg.appendChild(svgElement('rect', { x: 61, y: 125, width: 1478, height: 874, rx: 9, fill: '#f8f1e3', stroke: '#6e4a2c', 'stroke-width': 2 }));
    svg.appendChild(svgElement('rect', { x: 76, y: 140, width: 1448, height: 74, rx: 9, fill: '#163b32' }));
    svg.appendChild(svgElement('circle', { cx: 117, cy: 177, r: 23, fill: '#f3bb4d' }));
    svg.appendChild(svgElement('text', { x: 117, y: 185, fill: '#274233', 'font-family': 'Arial,sans-serif', 'font-size': 23, 'font-weight': 700, 'text-anchor': 'middle' }, 'M'));
    svg.appendChild(svgElement('text', { x: 155, y: 173, fill: '#ffffff', 'font-family': 'Arial,sans-serif', 'font-size': 22, 'font-weight': 700 }, 'MERCADO DEMO'));
    svg.appendChild(svgElement('text', { x: 155, y: 195, fill: '#c9dbd0', 'font-family': 'Arial,sans-serif', 'font-size': 14 }, 'Calidad y variedad para todos'));
    svg.appendChild(svgElement('text', { x: 1490, y: 173, fill: '#c7d9ce', 'font-family': 'Arial,sans-serif', 'font-size': 13, 'text-anchor': 'end' }, 'EXHIBICIÓN · U4'));

    const startX = 76;
    const startY = 230;
    const cellW = 174;
    const cellH = 174;
    const gapX = 8;
    const gapY = 8;

    state.slots.forEach((productId, index) => {
      const row = Math.floor(index / COLUMNS);
      const column = index % COLUMNS;
      const x = startX + column * (cellW + gapX);
      const y = startY + row * (cellH + gapY);
      const product = productById(productId);

      svg.appendChild(svgElement('rect', { x: x, y: y, width: cellW, height: cellH, rx: 5, fill: '#fffdf7', stroke: '#d4b48d', 'stroke-width': 2 }));
      svg.appendChild(svgElement('text', { x: x + 10, y: y + 18, fill: '#9a8268', 'font-family': 'Arial,sans-serif', 'font-size': 11, 'font-weight': 700 }, String(index + 1).padStart(2, '0')));

      if (product) {
        svg.appendChild(svgElement('use', { href: '#' + product.symbol, x: x + 37, y: y + 24, width: 100, height: 100 }));
        svg.appendChild(svgElement('text', { x: x + cellW / 2, y: y + 137, fill: '#34443b', 'font-family': 'Arial,sans-serif', 'font-size': 13, 'font-weight': 700, 'text-anchor': 'middle' }, product.name));
        svg.appendChild(svgElement('rect', { x: x + 48, y: y + 145, width: 78, height: 20, rx: 10, fill: '#e8f2ec', stroke: '#c7d9ce', 'stroke-width': 1 }));
        svg.appendChild(svgElement('text', { x: x + cellW / 2, y: y + 159, fill: '#1e5a48', 'font-family': 'Arial,sans-serif', 'font-size': 12, 'font-weight': 800, 'text-anchor': 'middle' }, money(product.price)));
      } else {
        svg.appendChild(svgElement('text', { x: x + cellW / 2, y: y + 96, fill: '#b29b7c', 'font-family': 'Arial,sans-serif', 'font-size': 34, 'text-anchor': 'middle' }, '+'));
        svg.appendChild(svgElement('text', { x: x + cellW / 2, y: y + 145, fill: '#ad9b84', 'font-family': 'Arial,sans-serif', 'font-size': 13, 'text-anchor': 'middle' }, 'Espacio libre'));
      }
    });

    svg.appendChild(svgElement('rect', { x: 76, y: 965, width: 1448, height: 22, rx: 3, fill: '#81552f' }));
    svg.appendChild(svgElement('text', { x: 90, y: 981, fill: '#f4e6cd', 'font-family': 'Arial,sans-serif', 'font-size': 11, 'font-weight': 700, 'letter-spacing': 2 }, 'EXHIBICIÓN DE PRODUCTOS'));
    svg.appendChild(svgElement('text', { x: 1510, y: 981, fill: '#f4e6cd', 'font-family': 'Arial,sans-serif', 'font-size': 11, 'font-weight': 700, 'letter-spacing': 1, 'text-anchor': 'end' }, 'SIMULACIÓN ACADÉMICA'));

    const serialized = new XMLSerializer().serializeToString(svg);
    const svgBlob = new Blob([serialized], { type: 'image/svg+xml;charset=utf-8' });
    const objectUrl = URL.createObjectURL(svgBlob);
    try {
      const image = new Image();
      await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = () => reject(new Error('El navegador no pudo renderizar la imagen del anaquel.'));
        image.src = objectUrl;
      });
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('No se pudo crear el lienzo de exportación.');
      context.drawImage(image, 0, 0, width, height);
      const pngBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      if (!pngBlob) throw new Error('No se pudo generar el archivo PNG.');
      downloadBlob(pngBlob, fileBaseName() + '.png');
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
    setExportStatus('PNG descargado. Usa JSON o CSV para guardar los datos de referencia.');
  } catch (error) {
    setExportStatus('Error al exportar PNG: ' + error.message);
  } finally {
    elements.png.disabled = false;
  }
}

function setExportStatus(message) {
  elements.exportStatus.textContent = message;
}

elements.apply.addEventListener('click', applySelection);
elements.empty.addEventListener('click', emptySelectedSlot);
elements.random.addEventListener('click', randomDistribution);
elements.clear.addEventListener('click', clearShelf);
elements.scenarioButton.addEventListener('click', () => applyScenario(elements.scenarioSelect.value));
elements.presentation.addEventListener('click', toggleCaptureMode);
elements.captureExit.addEventListener('click', toggleCaptureMode);
elements.png.addEventListener('click', exportPng);
elements.json.addEventListener('click', exportJson);
elements.csv.addEventListener('click', exportCsv);

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && state.captureMode) toggleCaptureMode();
});

applyScenario('equilibrado');
