document.getElementById('analysis-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('corpus-file');
    const keywordsInput = document.getElementById('keywords');
    const submitBtn = e.target.querySelector('button');

    if (!fileInput.files[0]) return;

    // UI Transitions
    submitBtn.innerHTML = "Initializing Protocol...";
    submitBtn.disabled = true;
    
    setTimeout(() => {
        document.getElementById('upload-panel').classList.add('hidden');
        document.getElementById('progress-panel').classList.remove('hidden');
    }, 600);

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('keywords', keywordsInput.value);

    // Agent Simulation Data
    const agentLogs = {
        1: ["> Ingesting corpus data...", "> Initializing spaCy en_core_web_sm...", "> Tokenizing sentences...", "> Calculating positional metadata...", "STATUS: Preprocessing optimal."],
        2: ["> Connecting to Neural Engine...", "> Analyzing Gricean Maxims...", "> Detecting Speech Acts (Searle)...", "> Evaluating Politeness parameters...", "STATUS: Pragmatic vectors extracted."],
        3: ["> Mapping Lexical Semantics...", "> Identifying Register Shifts...", "> Clustering target keywords...", "> Checking semantic drift thresholds...", "STATUS: Semantic fields mapped."],
        4: ["> Booting Statistical Engine...", "> Calculating Type-Token Ratio...", "> Building Collocation Matrices (+/- 5 window)...", "> Normalizing frequencies...", "STATUS: Statistics compiled."],
        5: ["> Aggregating data streams...", "> Cross-referencing Pragmatics with Statistics...", "> Applying Critical Discourse Analysis...", "> Formulating final Markdown Report...", "STATUS: Report generated successfully."]
    };

    let apiResponseData = null;
    let apiCompleted = false;
    let apiError = null;

    // Start API Call in parallel
    fetch('/api/analyze', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if(data.error) throw new Error(data.error);
            apiResponseData = data;
            apiCompleted = true;
        })
        .catch(err => {
            console.error(err);
            apiError = err;
            apiCompleted = true;
        });

    // Orchestrate Visuals
    for (let i = 1; i <= 5; i++) {
        await simulateAgentWork(i, agentLogs[i]);
        
        // If we are at Agent 5, wait for actual API to finish before marking complete
        if (i === 5) {
            updateAgentConsole(i, "> Awaiting final server confirmation...<span class='cursor'></span>");
            while(!apiCompleted) {
                await new Promise(r => setTimeout(r, 500));
            }
            if (apiError) {
                updateAgentState(i, 'error');
                updateAgentConsole(i, `> CRITICAL ERROR: ${apiError.message}`);
                return; // halt
            } else {
                updateAgentConsole(i, "> Server confirmation received.<br>> Initiating Dashboard rendering...");
                await new Promise(r => setTimeout(r, 800));
            }
        }
        updateAgentState(i, 'completed');
    }

    // Reveal Dashboard
    setTimeout(() => {
        document.getElementById('progress-panel').classList.add('hidden');
        document.getElementById('results-panel').classList.remove('hidden');
        renderDashboard(apiResponseData);
    }, 1000);
});

async function simulateAgentWork(agentId, logs) {
    updateAgentState(agentId, 'processing');
    const consoleEl = document.getElementById(`console-${agentId}`);
    consoleEl.innerHTML = "";
    
    for (let j = 0; j < logs.length; j++) {
        const line = logs[j];
        // Simulate typing
        let currentText = consoleEl.innerHTML.replace("<span class=\"cursor\"></span>", "");
        consoleEl.innerHTML = currentText + "<br>" + "<span class='typing'></span><span class='cursor'></span>";
        
        const typingSpan = consoleEl.querySelector('.typing');
        for (let char of line) {
            typingSpan.textContent += char;
            await new Promise(r => setTimeout(r, 20 + Math.random() * 30)); // random typing speed
        }
        await new Promise(r => setTimeout(r, 300)); // pause between lines
    }
}

function updateAgentState(agentId, state) {
    const card = document.getElementById(`agent-${agentId}`);
    const badge = card.querySelector('.badge');
    
    card.classList.remove('processing', 'completed');
    
    if (state === 'processing') {
        card.classList.add('processing');
        badge.className = 'badge processing';
        badge.innerText = 'Processing';
    } else if (state === 'completed') {
        card.classList.add('completed');
        badge.className = 'badge completed';
        badge.innerText = 'Completed';
        const consoleEl = document.getElementById(`console-${agentId}`);
        consoleEl.innerHTML = consoleEl.innerHTML.replace("<span class=\"cursor\"></span>", "");
    } else if (state === 'error') {
        badge.className = 'badge';
        badge.style.background = 'rgba(255,0,0,0.2)';
        badge.style.color = '#ff0000';
        badge.innerText = 'Failed';
    }
}

function updateAgentConsole(agentId, html) {
    const consoleEl = document.getElementById(`console-${agentId}`);
    consoleEl.innerHTML = consoleEl.innerHTML.replace("<span class=\"cursor\"></span>", "") + "<br>" + html;
}

function renderDashboard(data) {
    const reportHtml = marked.parse(data.report || "No report generated.");
    document.getElementById('markdown-content').innerHTML = reportHtml;

    if (data.stats && data.stats.keyword_frequencies) {
        const ctx = document.getElementById('driftChart').getContext('2d');
        const freqs = data.stats.keyword_frequencies;
        
        // Define futuristic gradient for the bar chart
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 240, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(112, 0, 255, 0.4)');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(freqs),
                datasets: [{
                    label: 'Target Keyword Frequency Matrix',
                    data: Object.values(freqs),
                    backgroundColor: gradient,
                    borderColor: '#00f0ff',
                    borderWidth: 1,
                    borderRadius: 4,
                    hoverBackgroundColor: '#00f0ff'
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { labels: { color: '#e2e8f0', font: { family: 'Outfit' } } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#8b95a5', font: { family: 'Outfit' } },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    x: {
                        ticks: { color: '#e2e8f0', font: { family: 'Outfit' } },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Attach Download JSON Logic
    if (data.raw_data) {
        const downloadBtn = document.getElementById('download-json');
        downloadBtn.onclick = () => {
            const jsonStr = JSON.stringify(data.raw_data, null, 2);
            const blob = new Blob([jsonStr], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pmdd_analysis_raw.json`;
            a.click();
            URL.revokeObjectURL(url);
        };
    }
}
