(function () {
  function initTravelMap() {
    const el = document.getElementById('travel-map');
    if (!el || typeof L === 'undefined') return null;

    const raw = el.getAttribute('data-markers') || '[]';
    let markers = [];
    try {
      markers = JSON.parse(raw);
    } catch (e) {
      markers = [];
    }

    const map = L.map(el, { scrollWheelZoom: false }).setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 18,
    }).addTo(map);

    const bounds = [];
    markers.forEach((m) => {
      if (m.lat == null || m.lng == null) return;
      const marker = L.marker([m.lat, m.lng]).addTo(map);
      const score = m.score ? ` · Gem ${m.score}/100` : '';
      const popup = `<strong>${m.title || 'Destination'}</strong><br>${m.category || ''}${score}`;
      if (m.url && m.url !== '#') {
        marker.bindPopup(`${popup}<br><a href="${m.url}">View post</a>`);
      } else {
        marker.bindPopup(popup);
      }
      bounds.push([m.lat, m.lng]);
    });

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [40, 40] });
    } else if (bounds.length === 1) {
      map.setView(bounds[0], 5);
    }

    return map;
  }

  let mapInstance = null;

  document.querySelectorAll('[data-view-toggle]').forEach((toggle) => {
    const cardsPanel = document.querySelector('[data-cards-panel]');
    const mapPanel = document.querySelector('[data-map-panel]');

    toggle.querySelectorAll('[data-view]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        toggle.querySelectorAll('[data-view]').forEach((b) => {
          b.classList.toggle('active', b === btn);
          b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
        });
        if (view === 'map') {
          if (cardsPanel) cardsPanel.classList.add('hidden');
          if (mapPanel) {
            mapPanel.classList.remove('hidden');
            if (!mapInstance) mapInstance = initTravelMap();
            setTimeout(() => mapInstance && mapInstance.invalidateSize(), 200);
          }
        } else {
          if (cardsPanel) cardsPanel.classList.remove('hidden');
          if (mapPanel) mapPanel.classList.add('hidden');
        }
      });
    });
  });
})();
