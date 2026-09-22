// NepaliCode Website JavaScript

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards
document.querySelectorAll('.feature-card, .example-item, .doc-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(card);
});

// Copy code functionality
document.querySelectorAll('.syntax-code, .install-code').forEach(codeBlock => {
    codeBlock.style.cursor = 'pointer';
    codeBlock.title = 'Click to copy';
    
    codeBlock.addEventListener('click', async () => {
        const code = codeBlock.textContent;
        try {
            await navigator.clipboard.writeText(code);
            codeBlock.title = 'Copied!';
            setTimeout(() => {
                codeBlock.title = 'Click to copy';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    });
});

// Mobile menu toggle (if needed in future)
const mobileMenuButton = document.querySelector('.mobile-menu-button');
if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', () => {
        const navLinks = document.querySelector('.nav-links');
        navLinks.classList.toggle('active');
    });
}

// Add loading animation
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
});

// Typing effect for hero subtitle (optional)
const heroSubtitle = document.querySelector('.hero-subtitle');
if (heroSubtitle) {
    const text = heroSubtitle.textContent;
    heroSubtitle.textContent = '';
    let i = 0;
    
    function typeWriter() {
        if (i < text.length) {
            heroSubtitle.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, 50);
        }
    }
    
    setTimeout(typeWriter, 1000);
}

// Console welcome message
console.log('%c🇳🇵 NepaliCode - Programming from Nepal', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%chttps://github.com/DiwasKhatri07/NepaliLang', 'font-size: 14px; color: #64748b;');