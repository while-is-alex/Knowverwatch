document.addEventListener('DOMContentLoaded', function() {
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
});
