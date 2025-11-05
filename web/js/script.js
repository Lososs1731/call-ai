/* ===================================
   COLDPIX - JAVASCRIPT
   =================================== */

// ===== THEME TOGGLE =====
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Check for saved theme preference or default to 'dark'
const currentTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const theme = html.getAttribute('data-theme');
    const newTheme = theme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Add rotation animation
    themeToggle.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        themeToggle.style.transform = 'rotate(0deg)';
    }, 300);
});

// ===== MOBILE MENU TOGGLE =====
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');

hamburger.addEventListener('click', () => {
    const isActive = navMenu.classList.toggle('active');
    hamburger.setAttribute('aria-expanded', isActive);
    
    // Animate hamburger icon
    const spans = hamburger.querySelectorAll('span');
    if (isActive) {
        spans[0].style.transform = 'rotate(45deg) translate(9px, 9px)';
        spans[1].style.opacity = '0';
        spans[1].style.transform = 'translateX(20px)';
        spans[2].style.transform = 'rotate(-45deg) translate(9px, -9px)';
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = 'hidden';
    } else {
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[1].style.transform = 'none';
        spans[2].style.transform = 'none';
        
        // Restore body scroll
        document.body.style.overflow = '';
    }
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
        
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[1].style.transform = 'none';
        spans[2].style.transform = 'none';
        
        // Restore body scroll
        document.body.style.overflow = '';
    });
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!navMenu.contains(e.target) && !hamburger.contains(e.target) && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
        
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[1].style.transform = 'none';
        spans[2].style.transform = 'none';
        
        document.body.style.overflow = '';
    }
});

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        
        if (target) {
            const navbarHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ===== NAVBAR SCROLL EFFECT =====
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        navbar.style.boxShadow = 'none';
        navbar.style.background = html.getAttribute('data-theme') === 'dark' 
            ? 'rgba(10, 10, 10, 0.85)' 
            : 'rgba(250, 250, 250, 0.85)';
    } else {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        navbar.style.background = html.getAttribute('data-theme') === 'dark' 
            ? 'rgba(10, 10, 10, 0.95)' 
            : 'rgba(250, 250, 250, 0.95)';
    }
    
    lastScroll = currentScroll;
});

// ===== DEMO FORM VALIDATION =====
const demoForm = document.getElementById('demoForm');

if (demoForm) {
    demoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = true;
        const formGroups = demoForm.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const input = group.querySelector('input');
            if (input && input.hasAttribute('required')) {
                if (!input.value.trim()) {
                    group.classList.add('error');
                    isValid = false;
                } else if (input.type === 'email' && !isValidEmail(input.value)) {
                    group.classList.add('error');
                    isValid = false;
                } else if (input.type === 'tel' && !isValidPhone(input.value)) {
                    group.classList.add('error');
                    isValid = false;
                } else {
                    group.classList.remove('error');
                }
            }
        });
        
        if (isValid) {
            // Show success message
            const btn = demoForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg><span>Voláme vám...</span>';
            btn.disabled = true;
            
            // Simulate call initiation
            setTimeout(() => {
                alert('Demo hovor byl zahájen! Prosím zvedněte telefon.');
                demoForm.reset();
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        }
    });
    
    // Real-time validation
    const inputs = demoForm.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            const formGroup = input.closest('.form-group');
            
            if (!input.value.trim()) {
                formGroup.classList.add('error');
            } else if (input.type === 'email' && !isValidEmail(input.value)) {
                formGroup.classList.add('error');
            } else if (input.type === 'tel' && !isValidPhone(input.value)) {
                formGroup.classList.add('error');
            } else {
                formGroup.classList.remove('error');
            }
        });
        
        input.addEventListener('input', () => {
            const formGroup = input.closest('.form-group');
            if (formGroup.classList.contains('error') && input.value.trim()) {
                formGroup.classList.remove('error');
            }
        });
    });
}

// ===== CONTACT FORM VALIDATION =====
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = true;
        const formGroups = contactForm.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const input = group.querySelector('input, textarea, select');
            if (input && input.hasAttribute('required')) {
                if (!input.value.trim()) {
                    group.classList.add('error');
                    isValid = false;
                } else if (input.type === 'email' && !isValidEmail(input.value)) {
                    group.classList.add('error');
                    isValid = false;
                } else {
                    group.classList.remove('error');
                }
            }
        });
        
        if (isValid) {
            const btn = contactForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg><span>Odesíláme...</span>';
            btn.disabled = true;
            
            setTimeout(() => {
                alert('Děkujeme za vaši zprávu! Brzy se vám ozveme.');
                contactForm.reset();
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 1500);
        }
    });
    
    // Real-time validation
    const inputs = contactForm.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            const formGroup = input.closest('.form-group');
            
            if (!input.value.trim()) {
                formGroup.classList.add('error');
            } else if (input.type === 'email' && !isValidEmail(input.value)) {
                formGroup.classList.add('error');
            } else {
                formGroup.classList.remove('error');
            }
        });
        
        input.addEventListener('input', () => {
            const formGroup = input.closest('.form-group');
            if (formGroup.classList.contains('error') && input.value.trim()) {
                formGroup.classList.remove('error');
            }
        });
    });
}

// ===== PRICING TOGGLE (Annual/Monthly) =====
const toggleBtns = document.querySelectorAll('.toggle-btn');
const priceAmounts = document.querySelectorAll('.price-amount');
const pricingSaves = document.querySelectorAll('.pricing-save');

toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const period = btn.getAttribute('data-period');
        
        // Update active state
        toggleBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update prices
        priceAmounts.forEach(amount => {
            const monthly = amount.getAttribute('data-monthly');
            const annual = amount.getAttribute('data-annual');
            
            if (period === 'annual') {
                amount.textContent = annual;
            } else {
                amount.textContent = monthly;
            }
        });
        
        // Update savings text
        pricingSaves.forEach(save => {
            if (period === 'annual') {
                save.style.opacity = '1';
            } else {
                save.style.opacity = '0';
            }
        });
    });
});

// ===== COUNTER ANIMATION FOR STATS =====
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px'
};

const animateCounter = (element) => {
    const target = parseFloat(element.getAttribute('data-count'));
    const isNegative = target < 0;
    const absTarget = Math.abs(target);
    const duration = 2000;
    const steps = 60;
    const increment = absTarget / steps;
    const stepDuration = duration / steps;
    let current = 0;
    
    const counter = setInterval(() => {
        current += increment;
        if (current >= absTarget) {
            current = absTarget;
            clearInterval(counter);
        }
        
        const displayValue = isNegative ? -Math.floor(current) : Math.floor(current);
        if (element.textContent.includes('%')) {
            element.textContent = displayValue + '%';
        } else if (element.textContent.includes('.')) {
            element.textContent = displayValue.toFixed(1) + '%';
        } else {
            element.textContent = displayValue;
        }
    }, stepDuration);
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && entry.target.hasAttribute('data-count')) {
            const hasAnimated = entry.target.hasAttribute('data-animated');
            if (!hasAnimated) {
                animateCounter(entry.target);
                entry.target.setAttribute('data-animated', 'true');
            }
        }
    });
}, observerOptions);

// Observe stat numbers
document.querySelectorAll('.stat-number[data-count]').forEach(stat => {
    observer.observe(stat);
});

// ===== UTILITY FUNCTIONS =====
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidPhone(phone) {
    const re = /^[0-9]{9}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// ===== SIMPLE AOS (Animate On Scroll) ALTERNATIVE =====
const fadeElements = document.querySelectorAll('[data-aos]');

const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

fadeElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    
    const delay = el.getAttribute('data-aos-delay');
    if (delay) {
        el.style.transitionDelay = `${delay}ms`;
    }
    
    fadeObserver.observe(el);
});

// ===== ESCAPE KEY TO CLOSE MOBILE MENU =====
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
        
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[1].style.transform = 'none';
        spans[2].style.transform = 'none';
        
        document.body.style.overflow = '';
    }
});

// ===== UPDATE NAVBAR BACKGROUND ON THEME CHANGE =====
const updateNavbarOnThemeChange = () => {
    const currentScroll = window.pageYOffset;
    const theme = html.getAttribute('data-theme');
    
    if (currentScroll > 0) {
        navbar.style.background = theme === 'dark' 
            ? 'rgba(10, 10, 10, 0.95)' 
            : 'rgba(250, 250, 250, 0.95)';
    } else {
        navbar.style.background = theme === 'dark' 
            ? 'rgba(10, 10, 10, 0.85)' 
            : 'rgba(250, 250, 250, 0.85)';
    }
};

// Watch for theme changes
const themeObserver = new MutationObserver(updateNavbarOnThemeChange);
themeObserver.observe(html, {
    attributes: true,
    attributeFilter: ['data-theme']
});

// ===== CONSOLE EASTER EGG =====
console.log('%c🚀 Coldpix AI Voice Bot', 'font-size: 24px; font-weight: bold; color: #0EA5E9;');
console.log('%cPowered by Scorpix | https://coldpix.cz', 'font-size: 14px; color: #64748B;');
console.log('%c💼 Hledáte práci? info@scorpix.cz', 'font-size: 12px; color: #10B981;');

// ===== INITIALIZE =====
console.log('✅ Coldpix initialized');