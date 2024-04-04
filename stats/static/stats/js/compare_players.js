document.addEventListener('DOMContentLoaded', function() {
    // Player A
    document.getElementById('player-a').addEventListener('change', function() {
        localStorage.setItem('selectedPlayerA', this.value);
        localStorage.removeItem('selectedHeroA');
        document.getElementById('player-a-form').submit();
    });

    document.getElementById('hero-a').addEventListener('change', function() {
        localStorage.setItem('selectedHeroA', this.value);
        document.getElementById('hero-a-form').submit();
    });

    // Player B
    document.getElementById('player-b').addEventListener('change', function() {
        localStorage.setItem('selectedPlayerB', this.value);
        localStorage.removeItem('selectedHeroB');
        document.getElementById('player-b-form').submit();
    });

    document.getElementById('hero-b').addEventListener('change', function() {
        localStorage.setItem('selectedHeroB', this.value);
        document.getElementById('hero-b-form').submit();
    });

    const selectedPlayerA = localStorage.getItem('selectedPlayerA');
    const selectedHeroA = localStorage.getItem('selectedHeroA');
    const selectedPlayerB = localStorage.getItem('selectedPlayerB');
    const selectedHeroB = localStorage.getItem('selectedHeroB');

    if (selectedPlayerA) {
        document.getElementById('player-a').value = selectedPlayerA;
    }

    if (selectedHeroA) {
        document.getElementById('hero-a').value = selectedHeroA;
    }

    if (selectedPlayerB) {
        document.getElementById('player-b').value = selectedPlayerB;
    }

    if (selectedHeroB) {
        document.getElementById('hero-b').value = selectedHeroB;
    }
});