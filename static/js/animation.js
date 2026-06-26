// ==========================================================================
// CURA Animations & UI Transitions (GSAP, Typed.js, Lottie Controls)
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. TYPED.JS WELCOME TEXT
    const typedWelcome = new Typed('#welcome-text-typed', {
        strings: [
            'Initializing Health Intelligence Core...',
            'Connecting SQLite Medical Logs...',
            'Rendering 3D Quantum Avatar...',
            'CURA is Ready. Beginning Consultation.'
        ],
        typeSpeed: 30,
        backSpeed: 10,
        loop: false,
        preStringTyped: (index, self) => {
            // Update progress bar at each string transition
            const progressSteps = [25, 55, 80, 100];
            const targetPercent = progressSteps[index] || 100;
            animateProgressBar(targetPercent);
        },
        onComplete: (self) => {
            setTimeout(completeLoadingSequence, 600);
        }
    });

    // 2. EKG HEARTBEAT WAVE LOADER
    const loaderContainer = document.getElementById('lottie-loader');
    if (loaderContainer) {
        loaderContainer.innerHTML = `
            <div class="ekg-container">
                <svg class="ekg-svg" viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <filter id="ekg-glow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="3" result="blur" />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>
                    <!-- Background static dim guide line -->
                    <path class="ekg-back" d="M 0 50 L 100 50 L 110 42 L 120 50 L 130 50 L 135 55 L 142 10 L 150 85 L 160 50 L 172 35 L 185 50 L 300 50" />
                    <!-- Foreground animated glowing pulse line -->
                    <path class="ekg-line" d="M 0 50 L 100 50 L 110 42 L 120 50 L 130 50 L 135 55 L 142 10 L 150 85 L 160 50 L 172 35 L 185 50 L 300 50" />
                </svg>
            </div>
        `;
        
        // Inject styles inline for the EKG heartbeat to keep style.css clean
        const style = document.createElement('style');
        style.textContent = `
            #lottie-loader {
                position: relative;
                width: 280px;
                height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 25px;
            }
            .ekg-container {
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .ekg-svg {
                width: 100%;
                height: 100%;
                overflow: visible;
            }
            .ekg-back {
                stroke: rgba(0, 240, 255, 0.08);
                stroke-width: 2;
                fill: none;
                stroke-linecap: round;
                stroke-linejoin: round;
            }
            .ekg-line {
                stroke: var(--text-cyan);
                stroke-width: 3;
                fill: none;
                stroke-linecap: round;
                stroke-linejoin: round;
                filter: url(#ekg-glow);
                stroke-dasharray: 100, 450;
                stroke-dashoffset: 550;
                animation: ekgSweep 1.6s linear infinite;
            }
            @keyframes ekgSweep {
                0% {
                    stroke-dashoffset: 550;
                }
                100% {
                    stroke-dashoffset: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
});

function animateProgressBar(percent) {
    const bar = document.getElementById('loading-progress');
    const label = document.getElementById('loading-percent');
    if (!bar || !label) return;

    // Use GSAP to animate numerical progress label and bar scale width
    gsap.to(bar, {
        width: `${percent}%`,
        duration: 0.6,
        ease: 'power1.out'
    });

    let currentVal = parseInt(label.innerText) || 0;
    gsap.to({ val: currentVal }, {
        val: percent,
        duration: 0.6,
        ease: 'power1.out',
        onUpdate: function() {
            label.innerText = `${Math.floor(this.targets()[0].val)}%`;
        }
    });
}

function completeLoadingSequence() {
    const screen = document.getElementById('loading-screen');
    const app = document.querySelector('.app-container');
    if (!screen || !app) return;

    // Fade out loader screen
    gsap.to(screen, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        onComplete: () => {
            screen.style.display = 'none';
            app.style.display = 'flex';
            
            // Trigger entry animation sequence
            animateEntranceTimeline();
        }
    });
}

function animateEntranceTimeline() {
    const tl = gsap.timeline();
    const isDesktop = window.innerWidth >= 1024;
    
    // Sidebar Slide-in (Desktop only to prevent absolute styling conflicts)
    if (isDesktop) {
        tl.fromTo('#sidebar', 
            { x: -320 }, 
            { x: 0, duration: 0.7, ease: 'power3.out' }
        );
    } else {
        // Clear any previous inline styles from GSAP to avoid conflict with CSS translateX
        gsap.set('#sidebar', { clearProps: 'all' });
    }

    // Header Slide-down
    tl.fromTo('.app-header', 
        { y: -70, opacity: 0 }, 
        { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' },
        isDesktop ? '-=0.4' : '0'
    );

    // Main widgets fade up (if they exist)
    if (document.querySelector('.left-column')) {
        tl.fromTo('.left-column > div', 
            { y: 30, opacity: 0 }, 
            { y: 0, opacity: 1, duration: 0.5, stagger: 0.15, ease: 'power2.out' },
            '-=0.3'
        );
    }

    // Chat card scale / fade in
    tl.fromTo('.chat-card', 
        { scale: 0.95, opacity: 0 }, 
        { scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(1.1)' },
        '-=0.4'
    );

    // Trigger welcoming bot speech and visual wave
    setTimeout(() => {
        // Welcome message animation trigger
        animateBotWelcomeText();
    }, 100);
}

function animateBotWelcomeText() {
    const welcomeBubble = document.getElementById('welcome-text-bot');
    if (!welcomeBubble) return;

    const msgText = "Hello! I am CURA, your AI Healthcare Assistant. I can help you check symptoms, retrieve medicine summaries, or provide healthy lifestyle suggestions. How can I assist you today? (Please note: I am an informational AI, not a doctor.)";

    // Play Typed.js on welcome bubble
    new Typed('#welcome-text-bot', {
        strings: [msgText],
        typeSpeed: 12,
        showCursor: false,
        onComplete: () => {
            // Setup Text To Speech for greeting if allowed
            if (typeof speakMessage === 'function') {
                speakMessage(msgText);
            }
        }
    });
}

// Animate new chat bubbles
function animateMessageBubble(msgElement, isUser) {
    const fromX = isUser ? 50 : -50;
    
    gsap.fromTo(msgElement, 
        { 
            x: fromX, 
            opacity: 0, 
            scale: 0.85 
        }, 
        { 
            x: 0, 
            opacity: 1, 
            scale: 1, 
            duration: 0.45, 
            ease: 'back.out(1.2)' 
        }
    );
}
