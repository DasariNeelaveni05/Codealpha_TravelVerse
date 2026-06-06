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

    (function() {
      const slides = document.querySelectorAll('.hero-slide');
      if (!slides.length) return;
      let current = 0;
      function nextSlide() {
        slides[current].classList.remove('active');
        current = (current + 1) % slides.length;
        slides[current].classList.add('active');
      }
      setInterval(nextSlide, 8000);
    })();

    const storiesRow = document.querySelector('.stories-row');
    if (storiesRow) {
      let isDown = false, startX, scrollLeft;
      storiesRow.addEventListener('mousedown', e => {
        isDown = true;
        startX = e.pageX - storiesRow.offsetLeft;
        scrollLeft = storiesRow.scrollLeft;
      });
      storiesRow.addEventListener('mouseleave', () => isDown = false);
      storiesRow.addEventListener('mouseup', () => isDown = false);
      storiesRow.addEventListener('mousemove', e => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - storiesRow.offsetLeft;
        storiesRow.scrollLeft = scrollLeft - (x - startX) * 1.5;
      });
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
      const current = phrases[phraseIndex];
      if (isDeleting) {
        typewriterEl.textContent = current.substring(0, charIndex - 1);
        charIndex--;
      } else {
        typewriterEl.textContent = current.substring(0, charIndex + 1);
        charIndex++;
      }
      let speed = isDeleting ? 60 : 100;
      if (!isDeleting && charIndex === current.length) {
        speed = 2000; isDeleting = true;
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        speed = 400;
      }
      setTimeout(type, speed);
    }
    if (typewriterEl) {
      type();
    }
    // --- END NEW TYPEWRITER HERO TEXT LOGIC ---

    // --- START NEW FLOATING PARTICLES LOGIC (from Part 3) ---
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      const particles = Array.from({length: 60}, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 3 + 1,
        speedX: (Math.random() - 0.5) * 0.4,
        speedY: -Math.random() * 0.6 - 0.2,
        opacity: Math.random() * 0.6 + 0.2,
        emoji: ['✈️','⭐','🌟','💫','✨'][Math.floor(Math.random()*5)]
      }));

      function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
          ctx.globalAlpha = p.opacity;
          ctx.font = `${p.size * 6}px serif`;
          ctx.fillText(p.emoji, p.x, p.y);
          p.x += p.speedX;
          p.y += p.speedY;
          if (p.y < -20) { p.y = canvas.height + 20; p.x = Math.random() * canvas.width; }
        });
        ctx.globalAlpha = 1;
        requestAnimationFrame(animateParticles);
      }
      animateParticles();
      window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      });
    }
    // --- END NEW FLOATING PARTICLES LOGIC ---

    // --- START NEW LIVE COUNTER ANIMATION LOGIC (from Part 3) ---
    function animateCounters() {
      document.querySelectorAll('.stat-number').forEach(el => {
        const target = parseInt(el.dataset.target);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = Math.floor(current).toLocaleString() + '+';
        }, 16);
      });
    }
    const statsBar = document.querySelector('.stats-bar');
    if (statsBar) {
      new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) animateCounters();
      }, {threshold: 0.5}).observe(statsBar);
    }
    // --- END NEW LIVE COUNTER ANIMATION LOGIC ---

    // --- START NEW SCROLL PROGRESS BAR LOGIC (from Part 3) ---
    window.addEventListener('scroll', () => {
      const el = document.getElementById('scroll-progress');
      if (el) {
        const pct = (window.scrollY / 
          (document.body.scrollHeight - window.innerHeight)) * 100;
        el.style.width = pct + '%';
      }
    });
    // --- END NEW SCROLL PROGRESS BAR LOGIC ---

    // --- START NEW GLOBAL SCROLL REVEAL LOGIC (from Part 3) ---
    const revealEls = document.querySelectorAll('.reveal');
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(el => io.observe(el));
    // --- END NEW GLOBAL SCROLL REVEAL LOGIC ---

    // --- START NEW LIKE BUTTON BOUNCE LOGIC (from Part 3) ---
    document.body.addEventListener('click', (e) => {
      const likeBtn = e.target.closest('.like-btn');
      if (likeBtn) {
        likeBtn.classList.add('bounce');
        likeBtn.addEventListener('animationend', () => likeBtn.classList.remove('bounce'), {once:true});
      }
    });
    // --- END NEW LIKE BUTTON BOUNCE LOGIC ---

    // Story Viewer Logic
    const storyViewer = document.getElementById('story-viewer');
    if (storyViewer) {
      const progressBar = document.getElementById('story-progress');
      let storyTimer;

      document.querySelectorAll('.ig-story-item').forEach(item => {
        item.addEventListener('click', (e) => {
          e.preventDefault();
          const ring = item.querySelector('.ig-story-avatar-ring');
          const username = ring.dataset.storyUsername;
          const avatar = ring.dataset.storyAvatar;
          const img = ring.dataset.storyImg;

          document.getElementById('story-viewer-username').textContent = username;
          document.getElementById('story-viewer-avatar').src = avatar;
          document.getElementById('story-viewer-img').src = img;

          storyViewer.classList.remove('hidden');
          progressBar.style.width = '0%';
          
          // Simple 5-second story animation
          progressBar.style.transition = 'width 5s linear';
          setTimeout(() => progressBar.style.width = '100%', 50);
          storyTimer = setTimeout(() => storyViewer.classList.add('hidden'), 5050);
        });
      });

      document.querySelector('.story-close').addEventListener('click', () => {
        storyViewer.classList.add('hidden');
        clearTimeout(storyTimer);
        progressBar.style.transition = 'none';
      });
    }
  });

  // --- START NEW REEL AUTOPLAY AND MUTE LOGIC (from Part 1) ---
  const reelFeed = document.querySelector('[data-reel-feed]');
  if (reelFeed) {
    const cards = Array.from(reelFeed.querySelectorAll('[data-reel-card]'));
    const reelObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const card = entry.target;
        const video = card.querySelector('.reel-video');
        const bgImg = card.querySelector('.reel-bg-image');
        if (!video && !bgImg) return;
        
        if (entry.isIntersecting && entry.intersectionRatio > 0.7) { // Changed threshold to 0.7
          if (video) {
            video.play().catch(() => {});
          }
          if (bgImg) {
            bgImg.classList.add('ken-burns-active');
          }
        } else {
          if (video) {
            video.pause();
            video.currentTime = 0;
          }
          if (bgImg) {
            bgImg.classList.remove('ken-burns-active');
          }
        }
      });
    }, { threshold: 0.7 });

    cards.forEach((card) => reelObserver.observe(card));

    // Hide swipe hint after first scroll (new logic)
    const hint = document.getElementById('swipe-hint');
    if (hint) {
      reelFeed.addEventListener('scroll', () => {
        hint.style.opacity = '0';
        setTimeout(() => hint.remove(), 500);
      }, { once: true });
    }
  }
  // --- END NEW REEL AUTOPLAY AND MUTE LOGIC ---

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
  document.body.addEventListener('click', async (e) => { // Changed to click for double-tap detection
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

  // --- START NEW DOUBLE-TAP HEART BURST LOGIC (from Part 3) ---
  let lastTap = 0;
  document.body.addEventListener('click', (e) => {
    const wrap = e.target.closest('.post-image-wrap');
    if (!wrap) return;

    const now = Date.now();
    if (now - lastTap < 300) {
      const heart = document.createElement('div');
      heart.innerHTML = '❤️';
      heart.className = 'floating-heart';
      heart.style.left = e.offsetX + 'px';
      heart.style.top = e.offsetY + 'px';
      wrap.appendChild(heart);
      setTimeout(() => heart.remove(), 1000);
      
      const postId = wrap.dataset.postId;
      const likeBtn = document.querySelector(`.like-btn[data-id="${postId}"]`);
      if (likeBtn) {
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
      if (scrollTop + clientHeight >= scrollHeight - 800) loadMore(); // Trigger earlier for smoother infinite scroll
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

  // --- START NEW PAGE TRANSITION LOGIC (from Part 3) ---
  document.querySelectorAll('a[href]').forEach(link => {
    // Only apply to internal links and exclude links with 'no-transition' class
    if (link.hostname === window.location.hostname && !link.classList.contains('no-transition')) {
      link.addEventListener('click', (e) => {
        const overlay = document.getElementById('page-overlay');
        if (overlay) {
          overlay.classList.add('active');
          setTimeout(() => { window.location.href = link.href; }, 250);
          e.preventDefault();
        }
      });
    }
  });
  window.addEventListener('pageshow', () => {
    const overlay = document.getElementById('page-overlay');
    if (overlay) overlay.classList.remove('active');
  });
  // --- END NEW PAGE TRANSITION LOGIC ---
})();
