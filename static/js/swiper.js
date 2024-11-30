document.addEventListener('DOMContentLoaded', () => {
  const swiper = new Swiper('.swiper', {
    loop: true,
    navigation: {
      nextEl: '#fr-slideshow-next',
      prevEl: '#fr-slideshow-prev',
    },
    pagination: {
      el: ".fr-slide-stepper",
      clickable: true,
      renderBullet: function (index, className) {
        return `<span class="${className}" 
                      tabindex="0" 
                      role="button" 
                      aria-label="Aller à la diapositive ${index + 1}"></span>`;
      },
    },
    a11y: {
      prevSlideMessage: 'Diapositive précédente',
      nextSlideMessage: 'Diapositive suivante',
      paginationBulletMessage: 'Aller à la diapositive {{index}}'
    },
  });
});