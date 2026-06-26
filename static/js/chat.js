// ==========================================================================
// CURA Chat System - API Integrations, Web Speech, & Dashboard Core
// ==========================================================================

let recognition;
let ttsEnabled = true;
let synth = window.speechSynthesis;
let voices = [];
let currentVoice = null;

// Dashboard States
let waterMax = 2500;
let waterLogged = 750;
let calMax = 2000;
let calLogged = 1200;
let sleepLogged = 7.5;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Dashboard UI
    loadDashboardState();
    
    // Core Event Handlers
    initChatControls();
    initSpeechSynthesis();
    initSpeechRecognition();
    initSidebarFeatures();
});

// ==========================================================================
// 1. Consultation & Chat logic
// ==========================================================================

function initChatControls() {
    const sendBtn = document.getElementById('send-msg-btn');
    const inputField = document.getElementById('chat-input-field');
    const ttsToggle = document.getElementById('voice-synthesis-toggle');

    // Auto resize textarea
    inputField.addEventListener('input', () => {
        inputField.style.height = 'auto';
        inputField.style.height = `${Math.min(inputField.scrollHeight, 100)}px`;
    });

    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // TTS Toggle Header Action
    ttsToggle.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        const icon = ttsToggle.querySelector('i');
        if (ttsEnabled) {
            icon.className = 'fa-solid fa-volume-high text-cyan';
            ttsToggle.title = "Mute Text-To-Speech";
        } else {
            icon.className = 'fa-solid fa-volume-xmark text-muted';
            ttsToggle.title = "Enable Text-To-Speech";
            if (synth) synth.cancel();
        }
    });

    // Emoji picker toggle
    const emojiBtn = document.getElementById('emoji-toggle-btn');
    const emojiPopup = document.getElementById('emoji-picker-container');
    emojiBtn.addEventListener('click', () => {
        emojiPopup.style.display = emojiPopup.style.display === 'none' ? 'block' : 'none';
    });

    // Mock file upload trigger
    const fileBtn = document.getElementById('file-upload-btn');
    const fileInput = document.getElementById('file-input');
    fileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            appendMessage(`[Uploaded attachment: ${fileInput.files[0].name}]`, true);
            showTypingIndicator();
            setTimeout(() => {
                hideTypingIndicator();
                appendMessage("Thank you for sharing the document. I have mapped this report data into your patient registry. Please describe your symptoms or request specific drug instructions.", false);
            }, 1200);
        }
    });
}

function sendMessage() {
    const inputField = document.getElementById('chat-input-field');
    const message = inputField.value.trim();
    if (!message) return;

    // Clear input
    inputField.value = '';
    inputField.style.height = 'auto';
    document.getElementById('emoji-picker-container').style.display = 'none';

    // Append user message bubble
    appendMessage(message, true);
    showTypingIndicator();

    // API Post to Flask app
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, user_id: 1 })
    })
    .then(res => res.json())
    .then(data => {
        hideTypingIndicator();
        if (data.error) {
            appendMessage(`Error: ${data.error}`, false);
            return;
        }

        // Append Bot message bubble
        appendMessage(data.response, false);

        // Control 3D Assistant Avatar
        if (typeof setExpression === 'function') {
            setExpression(data.animation);
        }
        if (data.animation === 'nod' && typeof triggerNod === 'function') {
            triggerNod();
        } else if (data.animation === 'wave' && typeof triggerWave === 'function') {
            triggerWave();
        }

        // Trigger Emergency mode UI if flagged
        if (data.emergency) {
            triggerEmergencyUI();
        } else {
            dismissEmergencyUI();
        }

        // Speak the response text
        const plainText = data.response.replace(/[#\*`💊⚠️🩺🥗🏃💧😴]/g, '').trim();
        speakMessage(plainText);

        // Refresh History list
        loadChatHistory();
    })
    .catch(err => {
        hideTypingIndicator();
        appendMessage("Network failure. Could not connect to CURA central servers.", false);
        console.error("Chat error:", err);
    });
}

function typeWriteHTML(element, htmlText, speed = 20, onComplete) {
    let index = 0;
    let currentHTML = "";
    
    // Tokenize HTML tags vs text content
    const tokens = [];
    let i = 0;
    while (i < htmlText.length) {
        if (htmlText[i] === '<') {
            let tag = "";
            while (i < htmlText.length && htmlText[i] !== '>') {
                tag += htmlText[i];
                i++;
            }
            if (i < htmlText.length) {
                tag += '>';
                i++;
            }
            tokens.push({ type: 'tag', val: tag });
        } else {
            let text = "";
            while (i < htmlText.length && htmlText[i] !== '<') {
                text += htmlText[i];
                i++;
            }
            // Split text by words/spaces
            const words = text.split(/(\s+)/);
            words.forEach(w => {
                if (w) tokens.push({ type: 'text', val: w });
            });
        }
    }
    
    function next() {
        if (index >= tokens.length) {
            if (onComplete) onComplete();
            return;
        }
        
        const token = tokens[index];
        if (token.type === 'tag') {
            currentHTML += token.val;
            element.innerHTML = currentHTML;
            index++;
            next(); // Tags render immediately
        } else {
            currentHTML += token.val;
            element.innerHTML = currentHTML;
            index++;
            
            const msgBox = document.getElementById('chat-messages');
            if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;
            
            // Adjust delay for natural pauses
            let delay = speed;
            if (token.val.includes('.') || token.val.includes('?') || token.val.includes('!')) {
                delay = speed * 8; // pause longer at end of sentences
            } else if (token.val.includes(',')) {
                delay = speed * 4;
            }
            
            setTimeout(next, delay);
        }
    }
    next();
}

window.sendSuggestedReply = function(text) {
    const input = document.getElementById('chat-input-field');
    if (input) {
        input.value = text;
        input.dispatchEvent(new Event('input'));
        sendMessage();
    }
};

function appendMessage(text, isUser) {
    const msgBox = document.getElementById('chat-messages');
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isUser ? 'user-message' : 'bot-message'}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'message-content-bubble';

    const textDiv = document.createElement('div');
    textDiv.className = 'chat-text';
    
    // Simple markdown to HTML parser
    let parsedText = text
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*)/g, '<li>$1</li>');
        
    if (parsedText.includes('<li>')) {
        // wrap lists
        parsedText = parsedText.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    
    // Replace newlines with <br> unless they're list items or headers
    parsedText = parsedText.split('\n').map(line => {
        if (line.trim().startsWith('<h') || line.trim().startsWith('<ul') || line.trim().startsWith('<li') || line.trim().startsWith('</ul')) {
            return line;
        }
        return line + '<br>';
    }).join('');

    bubble.appendChild(textDiv);

    // Timestamp
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const stamp = document.createElement('span');
    stamp.className = 'message-timestamp';
    stamp.innerText = timeStr;
    bubble.appendChild(stamp);

    // Save tip icon for bot messages containing lists or titles
    if (!isUser && (text.includes('###') || text.includes('- '))) {
        const bookmarkBtn = document.createElement('button');
        bookmarkBtn.className = 'save-tip-icon-btn';
        bookmarkBtn.title = "Save health recommendations";
        bookmarkBtn.innerHTML = '<i class="fa-regular fa-bookmark"></i>';
        bookmarkBtn.addEventListener('click', () => bookmarkHealthTip(text));
        bubble.appendChild(bookmarkBtn);
    }

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    msgBox.appendChild(wrapper);

    // Auto scroll chat
    msgBox.scrollTop = msgBox.scrollHeight;

    // Trigger GSAP bubble scale
    if (typeof animateMessageBubble === 'function') {
        animateMessageBubble(wrapper, isUser);
    }

    if (isUser) {
        textDiv.innerHTML = parsedText;
    } else {
        textDiv.innerHTML = "";
        typeWriteHTML(textDiv, parsedText, 25, () => {
            // Append suggested chips once bot finishes typing (skip for system alerts/warnings)
            if (!text.includes('GROQ_API_KEY') && !text.includes('CRITICAL EMERGENCY')) {
                const chipsDiv = document.createElement('div');
                chipsDiv.className = 'suggested-replies';
                chipsDiv.innerHTML = `
                    <button class="suggested-chip" onclick="sendSuggestedReply('Tell me more details')">Tell me more</button>
                    <button class="suggested-chip" onclick="sendSuggestedReply('What are some diet recommendations?')">Diet Advice</button>
                    <button class="suggested-chip" onclick="sendSuggestedReply('Show me some exercise suggestions')">Exercise Tips</button>
                    <button class="suggested-chip" onclick="sendSuggestedReply('I need emergency helpline details')">Emergency Help</button>
                `;
                bubble.appendChild(chipsDiv);
                
                // Refresh final scroll
                msgBox.scrollTop = msgBox.scrollHeight;
            }
        });
    }
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'flex';
    const msgBox = document.getElementById('chat-messages');
    msgBox.scrollTop = msgBox.scrollHeight;
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'none';
}

function insertEmoji(emoji) {
    const input = document.getElementById('chat-input-field');
    input.value += emoji;
    input.focus();
}

// ==========================================================================
// 2. Web Speech API (TTS & STT)
// ==========================================================================

function initSpeechSynthesis() {
    const voiceSelect = document.getElementById('voice-select');
    const rateSlider = document.getElementById('voice-rate');
    const rateLabel = document.getElementById('rate-val-label');
    const toggleVoiceModal = document.getElementById('voice-settings-toggle');

    toggleVoiceModal.addEventListener('click', () => {
        toggleModal('voice-settings-modal');
    });

    rateSlider.addEventListener('input', () => {
        rateLabel.innerText = `${rateSlider.value}x`;
    });

    // Load available browser voices
    function populateVoices() {
        if (!synth) return;
        voices = synth.getVoices();
        
        voiceSelect.innerHTML = '';
        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.innerText = `${voice.name} (${voice.lang})`;
            
            // Try to default to standard English voice
            if (voice.lang.includes('en-') && (voice.name.includes('Google') || voice.name.includes('Natural') || index === 0)) {
                option.selected = true;
                currentVoice = voice;
            }
            voiceSelect.appendChild(option);
        });
    }

    populateVoices();
    if (synth && synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = populateVoices;
    }

    voiceSelect.addEventListener('change', () => {
        currentVoice = voices[voiceSelect.value];
    });
}

function speakMessage(text) {
    const autoTTS = document.getElementById('voice-synthesis-enabled').checked;
    if (!synth || !ttsEnabled || !autoTTS) return;

    synth.cancel(); // Stop active speaking

    const utterance = new SpeechSynthesisUtterance(text);
    if (currentVoice) utterance.voice = currentVoice;
    
    const rateSlider = document.getElementById('voice-rate');
    utterance.rate = parseFloat(rateSlider.value) || 1.0;

    synth.speak(utterance);
}

function initSpeechRecognition() {
    const micBtn = document.getElementById('voice-input-btn');
    const inputField = document.getElementById('chat-input-field');

    // Standard API support check
    const SpeechSpeech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechSpeech) {
        micBtn.style.display = 'none';
        console.warn("Speech recognition is not supported in this browser.");
        return;
    }

    recognition = new SpeechSpeech();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('active')) {
            recognition.stop();
        } else {
            micBtn.classList.add('active');
            recognition.start();
        }
    });

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        inputField.value = text;
        micBtn.classList.remove('active');
        // trigger autosend or allow review
        inputField.dispatchEvent(new Event('input'));
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        micBtn.classList.remove('active');
    };

    recognition.onend = () => {
        micBtn.classList.remove('active');
    };
}

// ==========================================================================
// 3. Health Metric Trackers (BMI, Hydration, Sleep, Calories, ECG)
// ==========================================================================

function calculateBMI() {
    const weight = parseFloat(document.getElementById('bmi-weight').value);
    const height = parseFloat(document.getElementById('bmi-height').value);
    const resVal = document.getElementById('bmi-val');
    const resStatus = document.getElementById('bmi-status');

    if (!weight || !height) return;

    const bmi = weight / Math.pow(height / 100, 2);
    resVal.innerText = bmi.toFixed(1);

    let statusText = "Normal";
    let statusClass = "text-green";
    
    if (bmi < 18.5) {
        statusText = "Underweight";
        statusClass = "text-cyan";
    } else if (bmi >= 25 && bmi < 29.9) {
        statusText = "Overweight";
        statusClass = "text-orange";
    } else if (bmi >= 30) {
        statusText = "Obese";
        statusClass = "text-red";
    }

    resStatus.innerText = `(${statusText})`;
    resStatus.className = `sub-status ${statusClass}`;
    
    // Save to local storage
    localStorage.setItem('bmi_val', bmi.toFixed(1));
    localStorage.setItem('bmi_status', statusText);
}

function logWater(amount) {
    waterLogged = Math.min(waterLogged + amount, waterMax);
    const val = document.getElementById('water-logged');
    const wave = document.getElementById('water-wave');
    if (val) val.innerText = waterLogged;
    if (wave) wave.style.height = `${(waterLogged / waterMax) * 100}%`;
    localStorage.setItem('water_logged', waterLogged);
}

function resetWater() {
    waterLogged = 0;
    const val = document.getElementById('water-logged');
    const wave = document.getElementById('water-wave');
    if (val) val.innerText = 0;
    if (wave) wave.style.height = '0%';
    localStorage.setItem('water_logged', 0);
}

function addCalories() {
    const input = document.getElementById('cal-add-val');
    if (!input) return;
    const amount = parseInt(input.value);
    if (!amount) return;

    calLogged = Math.min(calLogged + amount, calMax);
    const val = document.getElementById('cal-logged');
    const progress = document.getElementById('calorie-progress');
    if (val) val.innerText = calLogged;
    if (progress) {
        const circumference = 2 * Math.PI * 25; // radius = 25
        const pct = (calLogged / calMax) * circumference;
        progress.style.strokeDashoffset = circumference - pct;
    }
    input.value = '';
    localStorage.setItem('cal_logged', calLogged);
}

function adjustSleep(val) {
    sleepLogged = Math.max(0, sleepLogged + val);
    const sleepVal = document.getElementById('sleep-logged');
    if (sleepVal) sleepVal.innerText = sleepLogged.toFixed(1);

    const qualityLabel = document.getElementById('sleep-quality');
    if (qualityLabel) {
        if (sleepLogged < 6) {
            qualityLabel.innerText = "Rest Deficit";
            qualityLabel.className = "sleep-quality text-orange";
        } else if (sleepLogged >= 6 && sleepLogged <= 9) {
            qualityLabel.innerText = "Optimal Rest";
            qualityLabel.className = "sleep-quality text-green";
        } else {
            qualityLabel.innerText = "Excessive Rest";
            qualityLabel.className = "sleep-quality text-cyan";
        }
    }
    localStorage.setItem('sleep_logged', sleepLogged);
}

function loadDashboardState() {
    const waterVal = document.getElementById('water-logged');
    const waterW = document.getElementById('water-wave');
    if (waterVal && waterW) {
        waterLogged = parseInt(localStorage.getItem('water_logged')) || 750;
        waterVal.innerText = waterLogged;
        waterW.style.height = `${(waterLogged / waterMax) * 100}%`;
    }

    const calVal = document.getElementById('cal-logged');
    const calP = document.getElementById('calorie-progress');
    if (calVal && calP) {
        calLogged = parseInt(localStorage.getItem('cal_logged')) || 1200;
        calVal.innerText = calLogged;
        const circumference = 2 * Math.PI * 25;
        calP.style.strokeDashoffset = circumference - ((calLogged / calMax) * circumference);
    }

    const sleepVal = document.getElementById('sleep-logged');
    if (sleepVal) {
        sleepLogged = parseFloat(localStorage.getItem('sleep_logged')) || 7.5;
        sleepVal.innerText = sleepLogged;
        adjustSleep(0); // updates color/label
    }

    const bmiV = document.getElementById('bmi-val');
    const bmiS = document.getElementById('bmi-status');
    if (bmiV && bmiS) {
        const savedBmi = localStorage.getItem('bmi_val');
        if (savedBmi) {
            bmiV.innerText = savedBmi;
            const savedStatus = localStorage.getItem('bmi_status') || 'Normal';
            bmiS.innerText = `(${savedStatus})`;
            
            let colorClass = 'text-green';
            if (savedStatus === 'Underweight') colorClass = 'text-cyan';
            if (savedStatus === 'Overweight') colorClass = 'text-orange';
            if (savedStatus === 'Obese') colorClass = 'text-red';
            bmiS.className = `sub-status ${colorClass}`;
        }
    }
}

// ==========================================================================
// 4. Emergency Mode Triggering
// ==========================================================================

function triggerEmergencyUI() {
    const banner = document.getElementById('emergency-banner');
    banner.style.display = 'block';
    
    // Glow border red on chat card
    const chatCard = document.querySelector('.chat-card');
    chatCard.style.borderColor = 'var(--text-red)';
    chatCard.style.boxShadow = '0 0 25px rgba(255, 51, 102, 0.25)';

    // Play GSAP banner entry shake
    gsap.fromTo(banner, 
        { scaleY: 0, opacity: 0 },
        { scaleY: 1, opacity: 1, transformOrigin: 'top', duration: 0.4, ease: 'power2.out' }
    );
}

function dismissEmergencyUI() {
    const banner = document.getElementById('emergency-banner');
    if (banner.style.display === 'none') return;
    
    gsap.to(banner, {
        scaleY: 0,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: () => {
            banner.style.display = 'none';
            // restore borders
            const chatCard = document.querySelector('.chat-card');
            chatCard.style.borderColor = 'var(--border-glass)';
            chatCard.style.boxShadow = 'none';
        }
    });
}

function findNearestHospitals() {
    // Open a mock maps directory search for clinics/hospitals
    window.open("https://www.google.com/maps/search/hospitals+near+me", "_blank");
}

// ==========================================================================
// 5. Sidebar and Configuration settings
// ==========================================================================

function initSidebarFeatures() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const profileBtn = document.getElementById('profile-toggle');
    const configBtn = document.getElementById('sidebar-settings-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // Mobile slide sidebar toggle
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    profileBtn.addEventListener('click', () => toggleModal('profile-modal'));
    configBtn.addEventListener('click', () => toggleModal('voice-settings-modal'));
    
    newChatBtn.addEventListener('click', () => {
        // Clear chat panel and introduce new chat
        const msgBox = document.getElementById('chat-messages');
        msgBox.innerHTML = `
            <div class="message-wrapper bot-message">
                <div class="message-avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="message-content-bubble">
                    <div class="chat-text">Welcome back. New consultation logs initialized. What physiological symptoms or drug catalog questions do you have?</div>
                    <span class="message-timestamp">Just now</span>
                </div>
            </div>
        `;
        dismissEmergencyUI();
        if (typeof resetAvatarState === 'function') resetAvatarState();
        if (typeof triggerWave === 'function') triggerWave();
    });

    clearHistoryBtn.addEventListener('click', () => {
        toggleModal('clear-confirm-modal');
    });

    const confirmClearActionBtn = document.getElementById('confirm-clear-action-btn');
    if (confirmClearActionBtn) {
        confirmClearActionBtn.addEventListener('click', () => {
            fetch('/history/clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 1 })
            })
            .then(res => res.json())
            .then(data => {
                loadChatHistory();
                
                // Reset active chat conversation panel visually
                const msgBox = document.getElementById('chat-messages');
                msgBox.innerHTML = `
                    <div class="message-wrapper bot-message">
                        <div class="message-avatar"><i class="fa-solid fa-robot"></i></div>
                        <div class="message-content-bubble">
                            <div class="chat-text">Consultation logs cleared. How can I assist you with your health today?</div>
                            <span class="message-timestamp">Just now</span>
                        </div>
                    </div>
                `;
                dismissEmergencyUI();
                toggleModal('clear-confirm-modal');
            });
        });
    }

    // Theme Toggle Handler (Light / Dark mode variables swap)
    const themeBtn = document.getElementById('theme-toggle');
    themeBtn.addEventListener('click', () => {
        const body = document.body;
        body.classList.toggle('light-mode');
        const isLight = body.classList.contains('light-mode');
        themeBtn.querySelector('i').className = isLight ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    });

    // Drug Index Search Bindings & Autocomplete
    const searchBtn = document.getElementById('med-search-btn');
    const searchInput = document.getElementById('med-search-input');
    const autocompleteDropdown = document.getElementById('med-autocomplete-dropdown');
    
    let debounceTimer;
    let activeSuggestionIndex = -1;
    let currentSuggestions = [];

    searchBtn.addEventListener('click', () => {
        hideAutocompleteDropdown();
        performDrugSearch();
    });

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const query = searchInput.value.trim();
        if (query.length < 2) {
            hideAutocompleteDropdown();
            return;
        }
        debounceTimer = setTimeout(() => {
            fetch(`/medicine/suggest?query=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(suggestions => {
                    currentSuggestions = suggestions;
                    renderAutocompleteDropdown(suggestions);
                })
                .catch(err => console.error("Autocomplete error:", err));
        }, 150);
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (currentSuggestions.length === 0) return;
            activeSuggestionIndex = (activeSuggestionIndex + 1) % currentSuggestions.length;
            highlightSuggestion();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (currentSuggestions.length === 0) return;
            activeSuggestionIndex = (activeSuggestionIndex - 1 + currentSuggestions.length) % currentSuggestions.length;
            highlightSuggestion();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (activeSuggestionIndex >= 0 && activeSuggestionIndex < currentSuggestions.length) {
                selectSuggestion(currentSuggestions[activeSuggestionIndex]);
            } else {
                hideAutocompleteDropdown();
                performDrugSearch();
            }
        } else if (e.key === 'Escape') {
            hideAutocompleteDropdown();
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !autocompleteDropdown.contains(e.target)) {
            hideAutocompleteDropdown();
        }
    });

    function renderAutocompleteDropdown(suggestions) {
        if (suggestions.length === 0) {
            hideAutocompleteDropdown();
            return;
        }
        activeSuggestionIndex = -1;
        autocompleteDropdown.innerHTML = '';
        suggestions.forEach((sug, idx) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                <div class="med-name">${sug.name}</div>
                <div class="generic-name">${sug.generic_name}</div>
            `;
            item.addEventListener('click', () => {
                selectSuggestion(sug);
            });
            autocompleteDropdown.appendChild(item);
        });
        autocompleteDropdown.style.display = 'block';
    }

    function highlightSuggestion() {
        const items = autocompleteDropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, idx) => {
            if (idx === activeSuggestionIndex) {
                item.classList.add('active');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    function selectSuggestion(sug) {
        searchInput.value = sug.name;
        hideAutocompleteDropdown();
        performDrugSearch();
    }

    function hideAutocompleteDropdown() {
        autocompleteDropdown.style.display = 'none';
        currentSuggestions = [];
        activeSuggestionIndex = -1;
    }

    // Load initial consultation records
    loadChatHistory();
}

window.searchForMedicine = function(name) {
    const input = document.getElementById('med-search-input');
    if (input) {
        input.value = name;
        performDrugSearch();
    }
};

function performDrugSearch() {
    const query = document.getElementById('med-search-input').value.trim();
    const resultsBox = document.getElementById('med-search-results');
    if (!query) return;

    resultsBox.innerHTML = '<span class="text-cyan"><i class="fa-solid fa-arrows-spin fa-spin"></i> Searching index...</span>';

    fetch(`/medicine?name=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
        if (!data.found) {
            if (data.has_suggestion) {
                resultsBox.innerHTML = `
                    <div style="text-align: left; font-size: 0.8rem;">
                        <span class="text-muted">Medicine not found.</span>
                        <button class="did-you-mean-btn" onclick="searchForMedicine('${data.suggestion.replace(/'/g, "\\'")}')">
                            Did you mean <strong>${data.suggestion}</strong>?
                        </button>
                    </div>
                `;
            } else {
                resultsBox.innerHTML = `<span class="text-red">${data.error}</span>`;
            }
            return;
        }

        // Render comprehensive drug profile
        resultsBox.innerHTML = `
            <div class="drug-profile-card">
                <div class="drug-title">💊 ${data.medicine_name || data.name}</div>
                <div class="drug-section"><span class="drug-label">Generic:</span> ${data.generic_name}</div>
                <div class="drug-section"><span class="drug-label">Category:</span> ${data.category}</div>
                <div class="drug-section"><span class="drug-label">Uses:</span> ${data.uses}</div>
                <div class="drug-section"><span class="drug-label">Mechanism:</span> ${data.how_it_works}</div>
                <div class="drug-section"><span class="drug-label">Dosage:</span> ${data.dosage}</div>
                <div class="drug-section"><span class="drug-label">How to Take:</span> ${data.how_to_take}</div>
                <div class="drug-section"><span class="drug-label">Common Side Effects:</span> ${data.common_side_effects}</div>
                <div class="drug-section"><span class="drug-label">Serious Side Effects:</span> ${data.serious_side_effects}</div>
                <div class="drug-section"><span class="drug-label">Precautions:</span> ${data.precautions}</div>
                <div class="drug-section"><span class="drug-label">Interactions:</span> ${data.interactions}</div>
                <div class="drug-section"><span class="drug-label">Warnings:</span> ${data.warnings}</div>
                <div class="drug-section"><span class="drug-label">Pregnancy Safety:</span> ${data.pregnancy_safety}</div>
                <div class="drug-section"><span class="drug-label">Breastfeeding Safety:</span> ${data.breastfeeding_safety}</div>
                <div class="drug-section"><span class="drug-label">Storage:</span> ${data.storage}</div>
                <div class="drug-disclaimer"><strong>Disclaimer:</strong> This information is for educational purposes only and is not a substitute for professional medical advice.</div>
            </div>
        `;
    })
    .catch(err => {
        resultsBox.innerHTML = '<span class="text-red">Error querying drug catalog.</span>';
        console.error("Drug search error:", err);
    });
}

function bookmarkHealthTip(text) {
    const list = document.getElementById('bookmarks-list');
    const emptyMsg = list.querySelector('.empty-bookmarks');
    if (emptyMsg) emptyMsg.remove();

    // Extract title (first line)
    const titleMatch = text.match(/### (.*)/) || text.match(/\*\*(.*?)\*\*/);
    const title = titleMatch ? titleMatch[1] : "General Advice";
    const cleanText = text.replace(/### (.*)/, '').trim().substring(0, 120) + "...";

    const bookmark = document.createElement('div');
    bookmark.className = 'bookmark-item';
    bookmark.innerHTML = `
        <h5>${title}</h5>
        <p>${cleanText}</p>
        <span class="remove-bookmark"><i class="fa-solid fa-xmark"></i></span>
    `;

    bookmark.querySelector('.remove-bookmark').addEventListener('click', (e) => {
        e.stopPropagation();
        bookmark.remove();
        if (list.children.length === 0) {
            list.innerHTML = '<div class="empty-bookmarks">Bookmarks empty. Save tips during chats!</div>';
        }
    });

    bookmark.addEventListener('click', () => {
        // paste into chat input
        document.getElementById('chat-input-field').value = `Tell me more details about: ${title}`;
    });

    list.appendChild(bookmark);
}

function loadChatHistory() {
    const list = document.getElementById('history-list');
    
    fetch('/history?user_id=1')
    .then(res => res.json())
    .then(data => {
        if (!data.history || data.history.length === 0) {
            list.innerHTML = '<div class="empty-history">No consultations yet.</div>';
            return;
        }

        list.innerHTML = '';
        data.history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            
            // Clean user message for history listing
            let displayMsg = item.message;
            if (displayMsg.length > 55) {
                displayMsg = displayMsg.substring(0, 52) + "...";
            }
            
            // Format time cleanly
            let timeStr = "";
            try {
                let tString = item.timestamp.replace(' ', 'T');
                const dateObj = new Date(tString);
                timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } catch(e) {
                timeStr = "Just now";
            }
            
            div.innerHTML = `
                <div class="history-item-header">
                    <span><i class="fa-regular fa-message text-cyan"></i> Consultation</span>
                    <span class="history-item-time">${timeStr}</span>
                </div>
                <div class="history-item-body">${displayMsg}</div>
            `;
            div.title = `Sent: ${item.message}\nReply: ${item.response}`;
            
            div.addEventListener('click', () => {
                // Restore values into input to allow prompt resending
                document.getElementById('chat-input-field').value = item.message;
            });
            list.appendChild(div);
        });
    })
    .catch(err => {
        console.error("Failed to load chat history:", err);
    });
}

// Save User Profile in JS
function saveUserProfile() {
    const name = document.getElementById('profile-name-input').value.trim();
    const email = document.getElementById('profile-email-input').value.trim();

    if (!name) return;

    fetch('/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, name: name, email: email })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Patient profile updated successfully.");
            toggleModal('profile-modal');
        }
    });
}

// Helpers
function toggleModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
}

