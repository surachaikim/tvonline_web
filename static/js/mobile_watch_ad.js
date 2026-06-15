(function () {
    var MOBILE_AD_URL = 'https://www.effectivecpmnetwork.com/d45azwef0?key=ddab2e8ffcab3864cd69681046ed90f9';
    var watchSelectors = [
        'a[href^="/live/"]',
        'a[href*="/live/"]',
        '.source-actions a',
        'a.source-button'
    ].join(',');

    function isMobileViewport() {
        return window.matchMedia('(max-width: 767.98px)').matches ||
            window.matchMedia('(pointer: coarse)').matches;
    }

    function isWatchLink(link) {
        if (!link || !link.matches) return false;
        if (!link.href || link.href === MOBILE_AD_URL) return false;
        return link.matches(watchSelectors);
    }

    document.addEventListener('click', function (event) {
        if (!isMobileViewport()) return;

        var link = event.target.closest ? event.target.closest('a') : null;
        if (!isWatchLink(link)) return;

        window.open(MOBILE_AD_URL, '_blank', 'noopener,noreferrer');
    }, true);
})();
