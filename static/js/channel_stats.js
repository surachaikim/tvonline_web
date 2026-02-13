/**
 * TVHUB — Channel Click Stats & Popular Ranking
 * Tracks channel clicks and displays "กำลังฮิต" section.
 */
(function () {
    /* ── Track clicks on "ดูสด" buttons ── */
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a.btn');
        if (!link) return;
        // Only track "ดูสด" buttons inside TV tab content
        var tvSection = document.getElementById('tvTabContent');
        if (!tvSection || !tvSection.contains(link)) return;
        var text = link.textContent.trim();
        if (!text.includes('ดูสด')) return;

        // Get channel info from parent card
        var card = link.closest('.card');
        if (!card) return;
        var title = card.querySelector('.card-title');
        var img = card.querySelector('img');
        if (!title) return;

        var channelName = title.textContent.trim();
        var channelLogo = img ? img.getAttribute('src') : '';
        var channelLink = link.getAttribute('href') || '';

        // Send click to server (fire-and-forget)
        fetch('/api/channel-click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: channelName, logo: channelLogo, link: channelLink })
        }).catch(function () { });
    });

    /* ── Render popular ranking section ── */
    function loadPopular() {
        var container = document.getElementById('popular-section');
        if (!container) return;

        fetch('/api/popular')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.channels || !data.channels.length) {
                    container.style.display = 'none';
                    return;
                }
                container.style.display = 'block';
                var html = '<h3 class="mb-3 text-center"><i class="bi bi-fire text-danger me-2"></i>กำลังฮิตตอนนี้</h3>';
                html += '<div class="row row-cols-2 row-cols-md-5 g-3 justify-content-center">';
                data.channels.forEach(function (ch, i) {
                    var badge = '';
                    if (i === 0) badge = '<span class="position-absolute top-0 start-0 badge bg-danger m-2">🥇 #1</span>';
                    else if (i === 1) badge = '<span class="position-absolute top-0 start-0 badge bg-warning text-dark m-2">🥈 #2</span>';
                    else if (i === 2) badge = '<span class="position-absolute top-0 start-0 badge bg-secondary m-2">🥉 #3</span>';
                    else badge = '<span class="position-absolute top-0 start-0 badge bg-dark m-2">#' + (i + 1) + '</span>';

                    html += '<div class="col">';
                    html += '<div class="card h-100 shadow-sm text-center position-relative popular-card">';
                    html += badge;
                    if (ch.logo) html += '<img src="' + ch.logo + '" class="card-img-top p-3" alt="' + ch.name + '" style="height:70px;object-fit:contain;">';
                    html += '<div class="card-body py-2">';
                    html += '<h6 class="card-title mb-1" style="font-size:.85rem">' + ch.name + '</h6>';
                    html += '<small class="text-muted">' + ch.clicks.toLocaleString() + ' views</small>';
                    html += '</div></div></div>';
                });
                html += '</div>';
                container.innerHTML = html;
            })
            .catch(function () { });
    }

    document.addEventListener('DOMContentLoaded', loadPopular);
})();
