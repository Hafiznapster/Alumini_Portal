// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Show page loading animation
    const body = document.querySelector('body');
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading';
    loadingScreen.innerHTML = '<div class="loader"></div>';
    body.appendChild(loadingScreen);
    
    // Hide loading screen after everything is loaded
    window.addEventListener('load', function() {
        setTimeout(function() {
            loadingScreen.style.opacity = '0';
            setTimeout(function() {
                loadingScreen.remove();
                
                // Animate content elements
                const animateElements = document.querySelectorAll('.card, .profile-header, h1, .alert');
                animateElements.forEach(function(element, index) {
                    setTimeout(function() {
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                    }, 100 * index);
                });
            }, 300);
        }, 500);
    });
    
    // Automatically close flash messages after 5 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        });
    }, 5000);

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    let forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password confirmation validation
    let passwordInput = document.getElementById('password');
    let confirmPasswordInput = document.getElementById('confirm_password');
    
    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            if (passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity("Passwords don't match");
            } else {
                confirmPasswordInput.setCustomValidity('');
            }
        });
    }

    // Dynamic event registration counter
    let registerButtons = document.querySelectorAll('.register-event-btn');
    registerButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            let countElement = document.getElementById('registration-count-' + this.dataset.eventId);
            if (countElement) {
                let currentCount = parseInt(countElement.textContent);
                countElement.textContent = currentCount + 1;
            }
        });
    });

    // Job search filter
    let jobSearchInput = document.getElementById('job-search');
    if (jobSearchInput) {
        jobSearchInput.addEventListener('input', function() {
            let searchTerm = this.value.toLowerCase();
            let jobCards = document.querySelectorAll('.job-card');
            
            jobCards.forEach(function(card) {
                let title = card.querySelector('.job-title').textContent.toLowerCase();
                let company = card.querySelector('.company').textContent.toLowerCase();
                let location = card.querySelector('.location').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || company.includes(searchTerm) || location.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Animated typing effect for hero section
    const heroText = document.querySelector('.hero-text');
    if (heroText) {
        const text = heroText.innerText;
        heroText.innerText = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroText.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };
        
        typeWriter();
    }
    
    // Image gallery modal and lightbox
    const galleryImages = document.querySelectorAll('.gallery-image');
    if (galleryImages.length > 0) {
        galleryImages.forEach(image => {
            image.addEventListener('click', function() {
                const modal = document.createElement('div');
                modal.className = 'lightbox-modal';
                modal.innerHTML = `
                    <div class="lightbox-content">
                        <span class="lightbox-close">&times;</span>
                        <img src="${this.src}" alt="${this.alt}" class="lightbox-img">
                        <p class="lightbox-caption">${this.alt}</p>
                    </div>
                `;
                document.body.appendChild(modal);
                
                // Add animation classes
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
                
                // Close the modal when clicking the close button or outside the image
                modal.addEventListener('click', function(e) {
                    if (e.target === modal || e.target.classList.contains('lightbox-close')) {
                        modal.classList.remove('show');
                        setTimeout(() => {
                            modal.remove();
                        }, 300);
                    }
                });
            });
        });
    }
    
    // Animated counters for statistics
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const observerOptions = {
            threshold: 0.5
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-count'));
                    const duration = 2000; // milliseconds
                    const step = Math.ceil(target / (duration / 20)); // Update every 20ms
                    let current = 0;
                    
                    const updateCounter = () => {
                        current += step;
                        if (current > target) current = target;
                        counter.innerText = current.toLocaleString();
                        
                        if (current < target) {
                            requestAnimationFrame(updateCounter);
                        } else {
                            observer.unobserve(counter);
                        }
                    };
                    
                    updateCounter();
                }
            });
        }, observerOptions);
        
        counters.forEach(counter => {
            observer.observe(counter);
        });
    }
    
    // Timeline animation for history/achievements
    const timelineItems = document.querySelectorAll('.timeline-item');
    if (timelineItems.length > 0) {
        const timelineObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('show');
                    timelineObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        timelineItems.forEach(item => {
            timelineObserver.observe(item);
        });
    }
    
    // Parallax scrolling effect for hero images
    const parallaxElements = document.querySelectorAll('.parallax');
    if (parallaxElements.length > 0) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.getAttribute('data-speed') || 0.5;
                element.style.transform = `translateY(${scrollPosition * speed}px)`;
            });
        });
    }
    
    // Interactive tabs with slide animation
    const tabLinks = document.querySelectorAll('.interactive-tabs .nav-link');
    if (tabLinks.length > 0) {
        tabLinks.forEach(link => {
            link.addEventListener('click', function() {
                const target = document.querySelector(this.getAttribute('data-bs-target'));
                const activeTab = document.querySelector('.interactive-tabs .tab-pane.show.active');
                
                if (activeTab && target && activeTab !== target) {
                    // Slide out current tab
                    activeTab.style.transform = 'translateX(-20px)';
                    activeTab.style.opacity = '0';
                    
                    // After animation completes, switch tabs and animate in
                    setTimeout(() => {
                        activeTab.classList.remove('show', 'active');
                        target.classList.add('show', 'active');
                        
                        // Reset position but invisible
                        target.style.transform = 'translateX(20px)';
                        target.style.opacity = '0';
                        
                        // Force reflow
                        void target.offsetWidth;
                        
                        // Animate in
                        target.style.transform = 'translateX(0)';
                        target.style.opacity = '1';
                    }, 300);
                }
            });
        });
    }
    
    // Interactive event calendar
    const calendarDays = document.querySelectorAll('.calendar-day');
    if (calendarDays.length > 0) {
        calendarDays.forEach(day => {
            if (day.getAttribute('data-events') > 0) {
                day.classList.add('has-events');
                
                day.addEventListener('click', function() {
                    const dayEvents = document.querySelector(`#events-${this.getAttribute('data-date')}`);
                    if (dayEvents) {
                        const allEvents = document.querySelectorAll('.day-events');
                        allEvents.forEach(el => {
                            if (el !== dayEvents) {
                                el.style.height = '0';
                                el.style.opacity = '0';
                                el.style.visibility = 'hidden';
                            }
                        });
                        
                        if (dayEvents.style.height === '0px' || !dayEvents.style.height) {
                            dayEvents.style.visibility = 'visible';
                            dayEvents.style.height = dayEvents.scrollHeight + 'px';
                            dayEvents.style.opacity = '1';
                        } else {
                            dayEvents.style.height = '0';
                            dayEvents.style.opacity = '0';
                            setTimeout(() => {
                                dayEvents.style.visibility = 'hidden';
                            }, 300);
                        }
                    }
                });
            }
        });
    }
    
    // Animated skill bars
    const skillBars = document.querySelectorAll('.skill-bar');
    if (skillBars.length > 0) {
        const skillObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target.querySelector('.progress-bar');
                    const percentage = progressBar.getAttribute('data-progress');
                    progressBar.style.width = percentage + '%';
                    skillObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        skillBars.forEach(bar => {
            skillObserver.observe(bar);
        });
    }

    // Initialize AOS animations
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.classList.add('ripple');
    });
    
    // Typing effect for hero text
    const heroText = document.querySelector('.hero-text');
    if (heroText) {
        const cursorElement = document.querySelector('.typing-cursor');
        if (cursorElement) {
            setInterval(() => {
                cursorElement.style.opacity = cursorElement.style.opacity === '0' ? '1' : '0';
            }, 500);
        }
    }
    
    // Stagger animation for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        const featuresContainer = featureCards[0].parentElement.parentElement.parentElement;
        featuresContainer.classList.add('stagger-in');
    }
    
    // Back to top button
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
}); 