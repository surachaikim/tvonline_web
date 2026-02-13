/**
 * TVHUB — Favorite Channels (LocalStorage)
 * Auto-detects channel info from existing card HTML structure.
 */
(function () {
    const STORAGE_KEY = 'tvhub_favorites';

    function getFavorites() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch { return []; }
    }

    function saveFavorites(favs) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(favs));
    }

    function isFavorite(id) {
        return getFavorites().some(f => f.id === id);
    }

    function toggleFavorite(channel) {
        let favs = getFavorites();
        const idx = favs.findIndex(f => f.id === channel.id);
        if (idx >= 0) {
            favs.splice(idx, 1);
        } else {
            favs.push(channel);
        }
        saveFavorites(favs);
        return idx < 0; // true = now favorited
    }

    /**
     * Extract channel info from a card element.
     * Works with the existing HTML: <img .card-img-top>, <h6 .card-title>, <a .btn>
     */
    function extractChannelInfo(card) {
        const img = card.querySelector('img.card-img-top, img');
        const title = card.querySelector('.card-title');
        const link = card.querySelector('a.btn');
        const source = card.querySelector('.card-body p');

        if (!title || !link) return null;

        const name = title.textContent.trim();
        const srcText = source ? source.textContent.trim() : '';
        const logo = img ? img.getAttribute('src') : '';
        const href = link.getAttribute('href') || '';
        // Create a unique ID from name + source
        const id = (name + '_' + srcText).replace(/\s+/g, '_').toLowerCase();

        return { id, name: name + (srcText ? ' (' + srcText + ')' : ''), logo, link: href };
    }

    /* ── Render the favorites section ── */
    function renderFavoritesSection() {
        const container = document.getElementById('favorites-section');
        if (!container) return;

        const favs = getFavorites();
        if (favs.length === 0) {
            container.innerHTML = '';
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        container.innerHTML = `
            <h3 class="mb-3 text-center">
                <i class="bi bi-star-fill text-warning me-2"></i>ช่องโปรดของคุณ
            </h3>
            <div class="row row-cols-2 row-cols-md-4 row-cols-lg-6 g-3 justify-content-center" id="fav-cards"></div>
        `;

        const row = container.querySelector('#fav-cards');
        favs.forEach(ch => {
            const col = document.createElement('div');
            col.className = 'col';
            col.innerHTML = `
                <div class="card h-100 shadow-sm text-center fav-glow">
                    <img src="${ch.logo}" class="card-img-top p-3" alt="${ch.name}"
                        style="height:80px;object-fit:contain;">
                    <div class="card-body py-2">
                        <h6 class="card-title mb-2" style="font-size:.85rem">${ch.name}</h6>
                        <a href="${ch.link}" class="btn btn-primary btn-sm" ${ch.link.startsWith('/') ? '' : 'target="_blank"'}>
                            <i class="bi bi-play-fill me-1"></i>ดูสด
                        </a>
                        <button class="btn btn-sm btn-outline-warning ms-1 fav-remove-btn" data-id="${ch.id}" title="ลบออกจากช่องโปรด">
                            <i class="bi bi-star-fill"></i>
                        </button>
                    </div>
                </div>
            `;
            row.appendChild(col);
        });

        // Remove handler
        row.querySelectorAll('.fav-remove-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = this.dataset.id;
                const ch = getFavorites().find(f => f.id === id);
                if (ch) toggleFavorite(ch);
                renderFavoritesSection();
                syncStars();
            });
        });
    }

    /* ── Inject ⭐ buttons into all TV channel cards ── */
    function initFavoriteButtons() {
        // Target cards inside the TV tabs sections
        const tvSection = document.getElementById('tvTabContent');
        if (!tvSection) return;

        tvSection.querySelectorAll('.card').forEach(card => {
            const info = extractChannelInfo(card);
            if (!info) return;

            const body = card.querySelector('.card-body');
            if (!body || body.querySelector('.fav-star-btn')) return;

            const btn = document.createElement('button');
            btn.className = 'btn btn-sm fav-star-btn';
            btn.dataset.channelId = info.id;
            btn.title = 'เพิ่ม/ลบช่องโปรด';
            btn.style.cssText = 'position:absolute;top:6px;right:6px;z-index:2;background:rgba(0,0,0,.5);border:none;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;';
            btn.innerHTML = isFavorite(info.id)
                ? '<i class="bi bi-star-fill text-warning"></i>'
                : '<i class="bi bi-star" style="color:#aaa"></i>';

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                const added = toggleFavorite(info);
                this.innerHTML = added
                    ? '<i class="bi bi-star-fill text-warning"></i>'
                    : '<i class="bi bi-star" style="color:#aaa"></i>';
                renderFavoritesSection();
            });

            // Make card position relative for the absolute star
            card.style.position = 'relative';
            card.appendChild(btn);
        });
    }

    function syncStars() {
        document.querySelectorAll('.fav-star-btn').forEach(btn => {
            const id = btn.dataset.channelId;
            if (!id) return;
            btn.innerHTML = isFavorite(id)
                ? '<i class="bi bi-star-fill text-warning"></i>'
                : '<i class="bi bi-star" style="color:#aaa"></i>';
        });
    }

    /* ── Init ── */
    document.addEventListener('DOMContentLoaded', function () {
        renderFavoritesSection();
        initFavoriteButtons();
    });
})();
