// ── CONFIG ───────────────────────────────────────────────────────────────────
const DEV_MODE = false;

// Approximate conversion rates (fallback when Amadeus test API returns USD/EUR
// despite the INR currency parameter). In production, fetch a live rate.
const USD_TO_INR = 83.5;
const EUR_TO_INR = 90.0;
const GBP_TO_INR = 105.0;

function toCurrencyINR(price, currency) {
  if (!price && price !== 0) return null;
  const p = parseFloat(price);
  if (isNaN(p)) return null;
  switch ((currency || '').toUpperCase()) {
    case 'INR': return p;
    case 'USD': return p * USD_TO_INR;
    case 'EUR': return p * EUR_TO_INR;
    case 'GBP': return p * GBP_TO_INR;
    default:
      // If value looks like USD (suspiciously small for INR), convert
      return p < 500 ? p * USD_TO_INR : p;
  }
}

function formatINR(amount) {
  if (amount == null || isNaN(amount)) return 'N/A';
  return '₹' + Math.round(amount).toLocaleString('en-IN');
}

function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}

function debugLog(...args) { if (DEV_MODE) console.log(...args); }

// ── CSRF ─────────────────────────────────────────────────────────────────────
function getCsrfToken() {
  const el = document.querySelector('input[name="csrf_token"]');
  return el ? el.value : '';
}

// ── MAIN ─────────────────────────────────────────────────────────────────────
let chatListenerAttached = false;

document.addEventListener('DOMContentLoaded', function () {
  const searchForm  = document.getElementById('search-form');
  const flightsList = document.getElementById('flights-list');
  const hotelsList  = document.getElementById('hotels-list');
  const loading     = document.getElementById('loading');
  const noFlights   = document.getElementById('no-flights');
  const noHotels    = document.getElementById('no-hotels');
  const flightsTitle = document.querySelector('.section-icon.flights')?.parentElement?.querySelector('.section-title');
  const hotelsTitle  = document.querySelector('.section-icon.hotels')?.parentElement?.querySelector('.section-title');
  const startPt     = document.getElementById('startPoint');
  const destEl      = document.getElementById('destination');
  const budgetTip   = document.getElementById('budget-tooltip');
  const startDate   = document.getElementById('startDate');
  const endDate     = document.getElementById('endDate');

  // Min date = today
  const today = new Date().toISOString().split('T')[0];
  if (startDate) startDate.min = today;
  if (endDate)   endDate.min   = today;

  // ── populate selects ────────────────────────────────────────────────────────
  function populateSelect(sel, cities) {
    if (!sel) return;
    const first = sel.options[0];
    sel.innerHTML = '';
    sel.appendChild(first);
    cities.forEach(c => {
      const opt = document.createElement('option');
      const label = `${c.name}, ${c.country}`;
      opt.value = label;
      opt.textContent = label;
      opt.setAttribute('data-city-code', c.city_code);
      sel.appendChild(opt);
    });
  }

  async function loadCities() {
    const cached = sessionStorage.getItem('availableCities');
    if (cached) {
      try {
        const cities = JSON.parse(cached);
        populateSelect(startPt, cities);
        populateSelect(destEl, cities);
        return;
      } catch (_) {}
    }
    try {
      const fd = new FormData();
      fd.append('csrf_token', getCsrfToken());
      const res   = await fetch('/search_cities', { method: 'POST', body: fd });
      const data  = await res.json();
      const cities = data.available_cities || data.suggestions || [];
      populateSelect(startPt, cities);
      populateSelect(destEl, cities);
      sessionStorage.setItem('availableCities', JSON.stringify(cities));
    } catch (e) {
      debugLog('loadCities error', e);
    }
  }

  loadCities();

  // ── min hotel price hint ────────────────────────────────────────────────────
  async function updateMinPrice() {
    if (!budgetTip) return;
    const dest   = destEl?.value;
    if (!dest) {
      budgetTip.textContent = 'Select destination to see min hotel cost';
      return;
    }
    budgetTip.textContent = 'Fetching min hotel cost…';
    const fd = new FormData();
    fd.append('csrf_token', getCsrfToken());
    fd.append('destination', dest);
    try {
      const res  = await fetch('/get_min_prices', { method: 'POST', body: fd });
      const data = await res.json();
      if (data.min_hotel_price && data.min_hotel_price !== 'N/A') {
        budgetTip.textContent = `Min hotel/night: ${data.min_hotel_price}`;
      } else {
        budgetTip.textContent = 'No price data available';
      }
    } catch (_) {
      budgetTip.textContent = '';
    }
  }

  startPt?.addEventListener('change', () => setTimeout(updateMinPrice, 50));
  destEl?.addEventListener('change',  () => setTimeout(updateMinPrice, 50));

  // ── render helpers ──────────────────────────────────────────────────────────
  function sourceBadge(source) {
    const s = (source || '').toLowerCase();
    if (['aviationstack', 'opensky', 'opentripmap'].includes(s)) {
      return `<span class="src-badge src-live">● Live</span>`;
    }
    if (s === 'ai_synthesized') {
      return `<span class="src-badge src-ai">✦ AI</span>`;
    }
    if (s === 'cached') {
      return `<span class="src-badge src-cached">◷ Cached</span>`;
    }
    if (s === 'static_fallback') {
      return `<span class="src-badge src-est">~ Est.</span>`;
    }
    return '';
  }

  function formatTime(iso) {
    if (!iso || iso === 'N/A') return '——';
    try {
      return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch (_) {
      return (iso.length >= 16) ? iso.slice(11, 16) : '——';
    }
  }

  function renderFlights(flights, sourceMeta) {
    flightsList.innerHTML = '';
    if (flightsTitle) flightsTitle.innerHTML = `Available flights ${sourceBadge(sourceMeta)}`;
    if (!flights || flights.length === 0) {
      if (noFlights) noFlights.style.display = 'block';
      return;
    }
    if (noFlights) noFlights.style.display = 'none';

    flights.forEach(f => {
      const priceINR = toCurrencyINR(f.price, f.currency);
      const priceStr = formatINR(priceINR);
      const dep     = formatTime(f.departureTime);
      const arr     = formatTime(f.arrivalTime);
      const airline = escapeHtml(f.airline || 'Unknown Airline');
      const fnum    = escapeHtml(f.flightNumber || '');
      const depAP   = escapeHtml(f.departureAirport || '—');
      const arrAP   = escapeHtml(f.arrivalAirport || '—');
      const rawDur  = f.duration || '';
      const dur     = rawDur
        ? escapeHtml(String(rawDur).replace('PT','').replace('H','h ').replace('M','m').trim())
        : '';
      const stopsN = Number.isFinite(Number(f.stops)) ? Number(f.stops) : 0;
      const stopsLabel = stopsN === 0 ? 'Non-stop' : `${stopsN} stop${stopsN === 1 ? '' : 's'}`;

      const div = document.createElement('div');
      div.className = 'flight-item';
      div.innerHTML = `
        <div class="fi-top">
          <span class="fi-airline">${airline}</span>
          ${fnum ? `<span class="fi-num">${fnum}</span>` : ''}
        </div>
        <div class="fi-route">
          <div class="fi-airport">
            <span class="fi-time">${dep}</span>
            <span class="fi-code">${depAP}</span>
          </div>
          <div class="fi-line">
            <div class="fi-line-bar"></div>
            <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3">
              <path d="M1 7s2.5-4.5 6-4.5S13 7 13 7s-2.5 4.5-6 4.5S1 7 1 7z"/>
              <circle cx="7" cy="7" r="1.5"/>
            </svg>
            <div class="fi-line-bar" style="background:linear-gradient(90deg,rgba(59,100,200,0.1),rgba(59,100,200,0.4))"></div>
          </div>
          <div class="fi-airport" style="text-align:right">
            <span class="fi-time">${arr}</span>
            <span class="fi-code">${arrAP}</span>
          </div>
        </div>
        <div class="fi-bottom">
          <span class="fi-price">${priceStr}</span>
          <span style="display:inline-flex;gap:8px;align-items:center">
            <span class="fi-stops ${stopsN === 0 ? 'fi-nonstop' : ''}">${stopsLabel}</span>
            ${dur ? `<span class="fi-duration">${dur}</span>` : ''}
          </span>
        </div>
      `;
      flightsList.appendChild(div);
    });
  }

  function renderHotels(hotels, sourceMeta) {
    hotelsList.innerHTML = '';
    if (hotelsTitle) hotelsTitle.innerHTML = `Hotels within budget ${sourceBadge(sourceMeta)}`;
    if (!hotels || hotels.length === 0) {
      if (noHotels) noHotels.style.display = 'block';
      return;
    }
    if (noHotels) noHotels.style.display = 'none';

    hotels.forEach(h => {
      const priceINR  = toCurrencyINR(h.price, h.currency);
      const priceStr  = formatINR(priceINR);
      const name      = escapeHtml(h.name || 'Hotel');
      const loc       = escapeHtml(h.location || '');
      const desc      = escapeHtml(h.description || '');
      const rating    = parseFloat(h.rating) || 0;
      const full      = Math.min(5, Math.round(rating));
      const stars     = '★'.repeat(full) + '☆'.repeat(5 - full);
      const amenities = Array.isArray(h.amenities) ? h.amenities : [];
      const isEst     = h.isEstimate;
      const overBudget = h.overBudget === true;

      const div = document.createElement('div');
      div.className = `hotel-item${overBudget ? ' over-budget' : ''}`;
      div.innerHTML = `
        <div class="hi-top">
          <span class="hi-name">${name}${isEst ? ' <span style="font-size:10px;color:rgba(255,180,50,0.5)">(est.)</span>' : ''} ${overBudget ? '<span class="budget-warn">↑ Over budget</span>' : ''}</span>
          <span class="hi-stars">${stars}</span>
        </div>
        ${loc ? `<div class="hi-location"><svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M6 1a3 3 0 010 6C3.3 7 1 4.5 1 4.5S3.3 1 6 1z"/><circle cx="6" cy="4" r="1"/></svg>${loc}</div>` : ''}
        ${desc ? `<div class="hi-desc">${desc}</div>` : ''}
        <div class="hi-bottom">
          <div class="hi-amenities">
            ${amenities.slice(0,4).map(a => `<span class="amenity-tag">${escapeHtml(String(a))}</span>`).join('')}
          </div>
          <div class="hi-price">
            <span class="hi-price-label">per night</span>
            <span class="hi-price-amount">${priceStr}</span>
          </div>
        </div>
      `;
      hotelsList.appendChild(div);
    });
  }

  // ── form submit ─────────────────────────────────────────────────────────────
  searchForm?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const startOpt  = startPt?.options[startPt.selectedIndex];
    const destOpt   = destEl?.options[destEl.selectedIndex];
    const startCode = startOpt?.getAttribute('data-city-code') || '';
    const destCode  = destOpt?.getAttribute('data-city-code') || '';
    const sd = startDate?.value;
    const ed = endDate?.value;

    if (!sd) { alert('Please select a departure date'); return; }
    if (ed && new Date(ed) <= new Date(sd)) { alert('Return date must be after departure date'); return; }
    if (!startCode || !destCode) { alert('Please select valid origin and destination'); return; }
    if (startCode === destCode) { alert('Origin and destination cannot be the same'); return; }

    if (loading) loading.style.display = 'block';
    flightsList.innerHTML = '';
    hotelsList.innerHTML  = '';
    if (noFlights) noFlights.style.display = 'none';
    if (noHotels)  noHotels.style.display  = 'none';

    const fd = new FormData(searchForm);
    fd.set('startPointCode', startCode);
    fd.set('destinationCode', destCode);

    try {
      const res  = await fetch('/search', { method: 'POST', body: fd });
      const data = await res.json();
      renderFlights(data.flights || [], data.meta?.flightSource);
      renderHotels(data.hotels  || [], data.meta?.hotelSource);
    } catch (err) {
      debugLog('search error', err);
      flightsList.innerHTML = '<p style="color:rgba(255,100,100,0.7);font-size:14px;padding:16px 0;">Error fetching results. Please try again.</p>';
    } finally {
      if (loading) loading.style.display = 'none';
    }
  });

  // Auto-advance return date on departure date change (default +7 days)
  startDate?.addEventListener('change', () => {
    const sd = startDate.value;
    if (!sd || !endDate) return;
    const sdDate = new Date(sd);
    const edVal = endDate.value;
    if (!edVal || new Date(edVal) <= sdDate) {
      const nd = new Date(sdDate);
      nd.setDate(nd.getDate() + 7);
      endDate.value = nd.toISOString().split('T')[0];
    }
    endDate.min = sd;
  });

  // ── chatbot ─────────────────────────────────────────────────────────────────
  const chatForm  = document.getElementById('chat-form');
  const chatInput = document.getElementById('userMessage');
  const chatMsgs  = document.getElementById('chat-messages');

  if (chatForm && !chatListenerAttached) {
    chatListenerAttached = true;

    chatForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const msg = chatInput?.value?.trim();
      if (!msg) return;

      // user bubble
      const userDiv = document.createElement('div');
      userDiv.className = 'message user';
      const ububble = document.createElement('div');
      ububble.className = 'msg-bubble';
      ububble.textContent = msg;
      userDiv.appendChild(ububble);
      chatMsgs.appendChild(userDiv);
      chatInput.value = '';
      chatMsgs.scrollTop = chatMsgs.scrollHeight;

      // typing indicator
      const typingDiv = document.createElement('div');
      typingDiv.className = 'message bot';
      typingDiv.innerHTML = `
        <div class="msg-avatar">
          <svg viewBox="0 0 13 13" fill="none" stroke="rgba(232,199,106,0.7)" stroke-width="1.2">
            <path d="M6.5 1a4 4 0 110 8 4 4 0 010-8z"/>
            <path d="M2 12c0-1.7 2-3 4.5-3s4.5 1.3 4.5 3"/>
          </svg>
        </div>
        <div class="msg-bubble" style="opacity:0.6">
          <span style="display:inline-flex;gap:4px;align-items:center">
            <span class="loader-dot"></span>
            <span class="loader-dot"></span>
            <span class="loader-dot"></span>
          </span>
        </div>`;
      chatMsgs.appendChild(typingDiv);
      chatMsgs.scrollTop = chatMsgs.scrollHeight;

      const fd = new FormData();
      fd.append('csrf_token', getCsrfToken());
      fd.append('message', msg);
      fd.append('destination', destEl?.value || '');
      fd.append('startPoint', startPt?.value || '');
      fd.append('startDate', startDate?.value || '');
      fd.append('endDate', endDate?.value || '');

      try {
        const res  = await fetch('/chatbot', { method: 'POST', body: fd });
        const data = await res.json();
        chatMsgs.removeChild(typingDiv);

        const botDiv = document.createElement('div');
        botDiv.className = 'message bot';
        const botBubble = document.createElement('div');
        botBubble.className = 'msg-bubble';
        const html = data.response || 'Sorry, I could not respond right now.';
        botBubble.innerHTML = typeof DOMPurify !== 'undefined' ? DOMPurify.sanitize(html) : html;
        botDiv.innerHTML = `<div class="msg-avatar"><svg viewBox="0 0 13 13" fill="none" stroke="rgba(232,199,106,0.7)" stroke-width="1.2"><path d="M6.5 1a4 4 0 110 8 4 4 0 010-8z"/><path d="M2 12c0-1.7 2-3 4.5-3s4.5 1.3 4.5 3"/></svg></div>`;
        botDiv.appendChild(botBubble);
        chatMsgs.appendChild(botDiv);
      } catch (_) {
        if (chatMsgs.contains(typingDiv)) chatMsgs.removeChild(typingDiv);
        const errDiv = document.createElement('div');
        errDiv.className = 'message bot';
        errDiv.innerHTML = `<div class="msg-avatar"><svg viewBox="0 0 13 13" fill="none" stroke="rgba(232,199,106,0.7)" stroke-width="1.2"><path d="M6.5 1a4 4 0 110 8 4 4 0 010-8z"/></svg></div><div class="msg-bubble" style="color:rgba(255,100,100,0.8)">Error reaching assistant. Try again.</div>`;
        chatMsgs.appendChild(errDiv);
      }
      chatMsgs.scrollTop = chatMsgs.scrollHeight;
    });
  }
});
