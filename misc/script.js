window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loading-screen');
    setTimeout(() => {
        loadingScreen.style.opacity = '0';
        loadingScreen.style.transition = 'opacity 0.5s ease';
        loadingScreen.addEventListener('transitionend', () => {
            loadingScreen.style.display = 'none';
        });
    }, 1500); // Adjust the delay as needed
});

// Optional: Auto-scroll the carousel
// Uncomment the following code if you want the carousel to auto-scroll

/*
const carousel = document.querySelector('.carousel');
let scrollAmount = 0;

function autoScroll() {
    if (scrollAmount <= carousel.scrollWidth - carousel.clientWidth) {
        carousel.scrollBy({
            top: 0,
            left: 200,
            behavior: 'smooth'
        });
    } else {
        carousel.scrollTo({
            top: 0,
            left: 0,
            behavior: 'smooth'
        });
    }
}

let scrollTimer = setInterval(autoScroll, 3000);

// Stop auto-scroll on mouse over
carousel.addEventListener('mouseover', () => {
    clearInterval(scrollTimer);
});

// Resume auto-scroll when mouse leaves
carousel.addEventListener('mouseout', () => {
    scrollTimer = setInterval(autoScroll, 3000);
});
*/

// // Add click handlers for all buttons
// document.addEventListener('DOMContentLoaded', () => {
//     const buttons = document.querySelectorAll('.btn');
//     buttons.forEach(button => {
//         button.addEventListener('click', (e) => {
//             e.preventDefault(); // Prevent immediate navigation
//             const pacmanOverlay = document.getElementById('pacman-overlay');
//             pacmanOverlay.style.display = 'flex';
            
//             // Navigate after animation
//             setTimeout(() => {
//                 window.location.href = button.href;
//             }, 2000); // Adjust timing as needed
//         });
//     });
// });