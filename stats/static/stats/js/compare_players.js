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

const prevButtons = document.querySelectorAll('.prev-button');
const nextButtons = document.querySelectorAll('.next-button');

prevButtons.forEach((prevButton, index) => {
    prevButton.addEventListener('click', () => {
        scrollHeroStatsContainer(index, -1);
    });
});

nextButtons.forEach((nextButton, index) => {
    nextButton.addEventListener('click', () => {
        scrollHeroStatsContainer(index, 1);
    });
});

function scrollHeroStatsContainer(index, direction) {
    const heroStatsContainers = document.querySelectorAll('.hero-stats-container');
    const heroStatsContainer = heroStatsContainers[index];
    const heroStatElements = heroStatsContainer.querySelectorAll('.hero-stat:not(.non-interactable)');

    const activeIndex = Array.from(heroStatElements).findIndex(heroStat => heroStat.classList.contains('active'));

    let nextIndex = activeIndex + direction;

    if (nextIndex < 0) {
        nextIndex = heroStatElements.length - 1;
    } else if (nextIndex >= heroStatElements.length) {
        nextIndex = 0;
    }

    heroStatElements[activeIndex].classList.remove('active');
    heroStatElements[nextIndex].classList.add('active');

    const heroStatWidth = heroStatElements[0].offsetWidth;
    const margin = 10;
    let newScrollLeft = nextIndex * (heroStatWidth + margin);

    heroStatsContainer.scrollLeft = newScrollLeft;
}
