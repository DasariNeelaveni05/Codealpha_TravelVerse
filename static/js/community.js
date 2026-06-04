(function () {
  const csrf = () =>
    window.CSRF_TOKEN ||
    document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  async function apiPost(url, body = {}) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf(),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  // Tab switching
  const tabs = document.querySelectorAll('.community-tab');
  const panels = document.querySelectorAll('.community-panel');

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      tabs.forEach((t) => t.classList.remove('active'));
      panels.forEach((p) => p.classList.remove('active'));

      tab.classList.add('active');
      const panel = document.getElementById(`panel-${target}`);
      if (panel) panel.classList.add('active');

      // Init map when map tab is shown
      if (target === 'map' && !window._communityMapInit) {
        initCommunityMap();
      }
    });
  });

  // Community Map
  function initCommunityMap() {
    const mapEl = document.getElementById('community-map');
    if (!mapEl) return;

    const map = L.map('community-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);

    // Add markers from context
    const markersData = window._communityMapMarkers || [];
    markersData.forEach((m) => {
      const marker = L.marker([m.lat, m.lng]).addTo(map);
      marker.bindPopup(
        `<strong>${m.title}</strong><br>` +
        `<span>Gem Score: ${m.score}/100</span><br>` +
        `<a href="${m.url}">View Post</a>`
      );
    });

    window._communityMapInit = true;

    // Fix map render after tab switch
    setTimeout(() => map.invalidateSize(), 100);
  }

  // Parse map markers from template
  const mapMarkersEl = document.querySelector('[data-map-markers]');
  if (mapMarkersEl) {
    try {
      window._communityMapMarkers = JSON.parse(mapMarkersEl.textContent);
    } catch (e) {
      window._communityMapMarkers = [];
    }
  }

  // Join Trip handler
  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-join-trip]');
    if (!btn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const tripId = btn.dataset.joinTrip;
    const data = await apiPost(`/api/trip/${tripId}/join/`, { message: '' });
    if (data.ok) {
      btn.textContent = 'Requested';
      btn.disabled = true;
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-outline');
    } else if (data.error) {
      btn.textContent = data.error.includes('already') ? 'Already Requested' : 'Error';
      btn.disabled = true;
    }
  });

  // Group join handler
  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-join-group]');
    if (!btn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const slug = btn.dataset.joinGroup;
    const data = await apiPost(`/api/group/${slug}/join/`);
    if (data.ok) {
      btn.textContent = data.joined ? 'Leave Group' : 'Join Group';
      btn.classList.toggle('btn-primary', !data.joined);
      btn.classList.toggle('btn-outline', data.joined);
      const countEl = btn.closest('.group-footer')?.querySelector('.group-members');
      if (countEl) countEl.textContent = `👥 ${data.count} members`;
    }
  });

  // Event RSVP handler
  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-rsvp-event]');
    if (!btn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const slug = btn.dataset.rsvpEvent;
    const data = await apiPost(`/api/event/${slug}/rsvp/`, { status: 'going' });
    if (data.ok) {
      btn.textContent = data.rsvped ? 'Going ✓' : 'RSVP';
      btn.classList.toggle('btn-primary', !data.rsvped);
      btn.classList.toggle('btn-outline', data.rsvped);
    }
  });
})();
