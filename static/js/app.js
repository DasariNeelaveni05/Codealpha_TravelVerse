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

  // Toast System
  function showToast(message, type = 'info') {
    const container = document.getElementById('tv-toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `tv-toast tv-toast-${type}`;
    
    // Choose icon based on type/content
    let icon = '🔔';
    if (message.toLowerCase().includes('like')) icon = '❤️';
    else if (message.toLowerCase().includes('follow')) icon = '🤝';
    else if (message.toLowerCase().includes('save') || message.toLowerCase().includes('bucket')) icon = '🗺️';
    else if (message.toLowerCase().includes('comment')) icon = '💬';
    else if (message.toLowerCase().includes('theme')) icon = '🎨';
    
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 400);
    }, 3000);
  }

  // Theme Management
  const themeToggle = document.getElementById('theme-toggle-btn');
  const themeMenu = document.getElementById('theme-menu');
  if (themeToggle && themeMenu) {
    themeToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      themeMenu.classList.toggle('show');
    });

    document.querySelectorAll('.theme-option').forEach(btn => {
      btn.addEventListener('click', () => {
        const theme = btn.dataset.themeVal;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('tv-selected-theme', theme);
        themeMenu.classList.remove('show');
        showToast(`Theme changed to ${btn.textContent.trim()}!`, 'success');
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', () => {
      themeMenu.classList.remove('show');
    });
  }

  // Load Persisted Theme
  const savedTheme = localStorage.getItem('tv-selected-theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  // Mobile Menu Hamburger Toggle
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const navLinks = document.getElementById('nav-links');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }

  // XP Progress Bar Loading Animation
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      document.querySelectorAll('.xp-bar-fill, .progress-fill').forEach(bar => {
        const widthVal = bar.style.width;
        if (widthVal) {
          bar.style.width = '0%';
          void bar.offsetWidth;
          bar.style.width = widthVal;
        }
      });
    }, 150);

    const heroBg = document.querySelector('.hero-bg');
    if (heroBg) {
      try {
        const slides = JSON.parse(heroBg.dataset.heroSlides || '[]');
        let active = 0;
        if (slides.length) {
          heroBg.style.backgroundImage = `url('${slides[0]}')`;
          setInterval(() => {
            active = (active + 1) % slides.length;
            heroBg.style.backgroundImage = `url('${slides[active]}')`;
          }, 7000);
        }
      } catch (err) {
        // ignore invalid JSON
      }
    }

    const typedEl = document.querySelector('.hero-typed');
    if (typedEl) {
      const phrases = [
        'Discover Hidden Gems',
        'Plan Your Adventure',
        'Connect With Explorers',
        'Share Your Journey',
        'Find Local Guides',
      ];
      let phraseIndex = 0;
      let charIndex = 0;
      const cursor = document.querySelector('.cursor');
      const typeNext = () => {
        const text = phrases[phraseIndex];
        if (charIndex <= text.length) {
          typedEl.textContent = text.slice(0, charIndex);
          charIndex += 1;
          setTimeout(typeNext, 90);
        } else {
          setTimeout(() => {
            charIndex = 0;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            typeNext();
          }, 1600);
        }
      };
      typeNext();
      if (cursor) cursor.classList.add('typing');
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle('visible', entry.isIntersecting);
      });
    }, { threshold: 0.25 });
    document.querySelectorAll('.animate-on-scroll').forEach((el) => observer.observe(el));

    const reelFeed = document.querySelector('[data-reel-feed]');
    if (reelFeed) {
      const cards = Array.from(reelFeed.querySelectorAll('[data-reel-card]'));
      const reelObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          const card = entry.target;
          const video = card.querySelector('video');
          const progress = card.querySelector('.reel-progress-fill');
          if (!video) return;
          if (entry.isIntersecting && entry.intersectionRatio > 0.65) {
            video.play().catch(() => {});
            if (progress && video.duration) {
              video.addEventListener('timeupdate', () => {
                progress.style.width = `${(video.currentTime / video.duration) * 100}%`;
              });
            }
          } else {
            video.pause();
          }
        });
      }, { threshold: [0.65] });

      cards.forEach((card) => reelObserver.observe(card));

      reelFeed.addEventListener('click', (e) => {
        const muteBtn = e.target.closest('.reel-mute-toggle');
        if (!muteBtn) return;
        const card = e.target.closest('[data-reel-card]');
        const video = card?.querySelector('video');
        if (!video) return;
        video.muted = !video.muted;
        muteBtn.textContent = video.muted ? '🔇' : '🔊';
      });
    }
  });

  // Like Toggle Handler
  document.body.addEventListener('click', async (e) => {
    const likeBtn = e.target.closest('[data-like]');
    if (!likeBtn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const id = likeBtn.dataset.like;
    const data = await apiPost(`/api/like/${id}/`);
    if (!data.ok) return;
    
    likeBtn.classList.toggle('liked', data.liked);
    likeBtn.querySelector('.icon-heart').textContent = data.liked ? '❤️' : '🤍';
    
    const countEl = document.querySelector(`[data-like-count="${id}"]`);
    if (countEl) countEl.textContent = `${data.count} likes`;
    
    const gemEl = document.querySelector(`[data-gem-score="${id}"]`);
    if (gemEl && data.gem_score !== undefined) {
      gemEl.innerHTML = `Gem score: <strong>${data.gem_score}</strong>/100`;
    }
    
    showToast(data.liked ? 'Post liked!' : 'Like removed', 'success');
  });

  document.body.addEventListener('click', async (e) => {
    const reelBtn = e.target.closest('[data-like-reel]');
    if (!reelBtn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const id = reelBtn.dataset.likeReel;
    const data = await apiPost(`/api/reel/like/${id}/`);
    if (!data.ok) return;
    reelBtn.classList.toggle('liked', data.liked);
    showToast(data.liked ? 'Reel liked!' : 'Reel removed', 'success');
  });

  // Double-tap Like with dynamic heart burst
  document.body.addEventListener('dblclick', async (e) => {
    const media = e.target.closest('[data-double-tap-like]');
    if (!media || !window.USER_AUTHENTICATED) return;
    
    const id = media.dataset.doubleTapLike;
    
    // Spawning floating heart burst at coordinates
    const rect = media.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const heart = document.createElement('div');
    heart.className = 'double-tap-heart';
    heart.innerHTML = '❤️';
    heart.style.left = `${x}px`;
    heart.style.top = `${y}px`;
    media.appendChild(heart);
    
    setTimeout(() => heart.remove(), 800);

    const btn = document.querySelector(`[data-like="${id}"]`);
    if (btn && !btn.classList.contains('liked')) {
      const data = await apiPost(`/api/like/${id}/`);
      if (data.ok) {
        btn.classList.add('liked');
        btn.querySelector('.icon-heart').textContent = '❤️';
        const countEl = document.querySelector(`[data-like-count="${id}"]`);
        if (countEl) countEl.textContent = `${data.count} likes`;
        showToast('Post liked!', 'success');
      }
    }
  });

  // Share link handler
  document.body.addEventListener('click', async (e) => {
    const shareBtn = e.target.closest('[data-share]');
    if (shareBtn) {
      e.preventDefault();
      const card = shareBtn.closest('[data-share-url]');
      const shareValue = shareBtn.dataset.share;
      const path = shareValue || card?.dataset?.shareUrl || window.location.pathname;
      const url = shareValue && shareValue.startsWith('http') ? shareValue : `${window.location.origin}${path}`;
      const title = 'TravelVerse – Hidden Gem';
      
      if (navigator.share) {
        try {
          await navigator.share({ title, url });
        } catch (err) {
          if (err.name !== 'AbortError') {
            await navigator.clipboard.writeText(url);
            showToast('Link copied to clipboard!', 'success');
          }
        }
      } else {
        await navigator.clipboard.writeText(url);
        showToast('Link copied to clipboard!', 'success');
      }
      return;
    }
  });

  // Follow Toggle Handler
  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-follow]');
    if (!btn || !window.USER_AUTHENTICATED) return;
    e.preventDefault();
    const username = btn.dataset.follow;
    const data = await apiPost(`/api/follow/${username}/`);
    if (!data.ok) return;
    
    btn.textContent = data.following ? 'Following' : 'Follow';
    btn.classList.toggle('following', data.following);
    btn.dataset.following = data.following;
    
    const fc = document.getElementById('followers-count');
    if (fc) fc.textContent = data.followers_count;
    
    showToast(data.following ? `Followed @${username}!` : `Unfollowed @${username}`, 'success');
  });

  // Save, bucket, gem vote
  const actions = {
    'data-save': (id) => `/api/save/${id}/`,
    'data-bucket': (id) => `/api/bucket/${id}/`,
    'data-gem-vote': (id) => `/api/gem-vote/${id}/`,
  };
  
  document.body.addEventListener('click', async (e) => {
    for (const [attr, urlFn] of Object.entries(actions)) {
      const btn = e.target.closest(`[${attr}]`);
      if (!btn || !window.USER_AUTHENTICATED) continue;
      e.preventDefault();
      const id = btn.getAttribute(attr);
      const data = await apiPost(urlFn(id));
      if (!data.ok) continue;
      
      if (attr === 'data-gem-vote') {
        const votes = document.querySelector(`[data-votes="${id}"]`);
        if (votes) votes.textContent = data.votes;
        showToast(data.voted ? 'Voted up hidden gem!' : 'Gem vote removed', 'success');
      } else if (attr === 'data-save') {
        showToast(data.saved ? 'Saved to collection!' : 'Removed from collection', 'success');
      } else if (attr === 'data-bucket') {
        showToast(data.saved ? 'Added to travel planner!' : 'Removed from travel planner', 'success');
      }
      
      if (data.saved !== undefined) btn.classList.toggle('active', data.saved);
      if (data.voted !== undefined) btn.classList.toggle('active', data.voted);
      if (data.gem_score !== undefined) {
        const gemEl = document.querySelector(`[data-gem-score="${id}"]`);
        if (gemEl) gemEl.innerHTML = `Gem score: <strong>${data.gem_score}</strong>/100`;
      }
      break;
    }
  });

  // Inline Comment Submission
  document.body.addEventListener('submit', async (e) => {
    const form = e.target.closest('[data-comment-form]');
    if (!form) return;
    e.preventDefault();
    const id = form.dataset.commentForm;
    const input = form.querySelector('input[name=text]');
    const text = input.value.trim();
    if (!text) return;
    const data = await apiPost(`/api/comment/${id}/`, { text });
    if (data.ok) {
      input.value = '';
      const countEl = document.querySelector(`[data-comment-count="${id}"]`);
      if (countEl) countEl.textContent = `${data.count} comments`;
      showToast('Comment posted successfully!', 'success');
      
      // Auto reload comments if detail page
      if (window.location.pathname.includes(`/post/${id}/`)) {
        setTimeout(() => location.reload(), 500);
      }
    }
  });

  // Infinite scroll feed
  const feed = document.querySelector('[data-feed]');
  const loader = document.getElementById('feed-loader');
  if (feed) {
    let loading = false;
    let nextPage = feed.dataset.nextPage;

    const loadMore = async () => {
      if (!nextPage || loading) return;
      loading = true;
      if (loader) loader.classList.remove('hidden');
      const url = new URL(window.location.href);
      url.searchParams.set('page', nextPage);
      const res = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await res.json();
      if (data.ok && data.html) {
        feed.insertAdjacentHTML('beforeend', data.html);
        nextPage = data.has_next ? data.next_page : null;
        feed.dataset.nextPage = nextPage || '';
      }
      loading = false;
      if (loader) loader.classList.add('hidden');
    };

    const onScroll = () => {
      if (!nextPage) return;
      const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
      if (scrollTop + clientHeight >= scrollHeight - 200) loadMore();
    };
    window.addEventListener('scroll', onScroll);
  }

  // Simple image carousel swipe hint
  document.querySelectorAll('[data-carousel]').forEach((el) => {
    let startX = 0;
    el.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });
    el.addEventListener('touchend', (e) => {
      const diff = startX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 40) el.scrollBy({ left: diff > 0 ? el.clientWidth : -el.clientWidth, behavior: 'smooth' });
    });
  });

  // Auto-hide flash messages
  document.querySelectorAll('.flash').forEach((el) => {
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });
})();
