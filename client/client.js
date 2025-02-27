class OmniParserClient {
    constructor(serverUrl = 'http://localhost:8000') {
        this.serverUrl = serverUrl;
        this.setupEventListeners();
    }

    setupEventListeners() {
        const fileInput = document.getElementById('imageInput');
        const parseButton = document.getElementById('parseButton');
        
        parseButton.addEventListener('click', () => this.parseImage());
        fileInput.addEventListener('change', () => this.handleFileSelect());
    }

    async checkServerHealth() {
        try {
            const response = await fetch(`${this.serverUrl}/health`);
            if (!response.ok) throw new Error('Server health check failed');
            return await response.json();
        } catch (error) {
            throw new Error(`Server not responding: ${error.message}`);
        }
    }

    async parseImage() {
        const fileInput = document.getElementById('imageInput');
        const resultsDiv = document.getElementById('results');
        const file = fileInput.files[0];

        if (!file) {
            this.showError('Please select an image file');
            return;
        }

        try {
            await this.checkServerHealth();
            
            const formData = new FormData();
            formData.append('file', file);

            // Show loading state
            resultsDiv.innerHTML = '<div class="loading">Processing image...</div>';

            const response = await fetch(`${this.serverUrl}/parse`, {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.displayResults(data.results);

        } catch (error) {
            this.showError(error.message);
        }
    }

    displayResults(results) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <h2>Parsing Results (${results.length} elements found):</h2>
            <div class="results-grid">
                ${results.map((result, index) => this.createResultCard(result, index)).join('')}
            </div>
        `;
    }

    createResultCard(result, index) {
        return `
            <div class="result-card">
                <h3>Element ${index + 1}</h3>
                <p class="caption">${result.caption}</p>
                <p class="location">Location: ${result.box.map(n => n.toFixed(2)).join(', ')}</p>
                <p class="confidence">Confidence: ${(result.confidence * 100).toFixed(1)}%</p>
            </div>
        `;
    }

    showError(message) {
        document.getElementById('results').innerHTML = `
            <div class="error">
                <h3>Error:</h3>
                <p>${message}</p>
                <p>Please ensure the server is running at ${this.serverUrl}</p>
            </div>
        `;
    }

    handleFileSelect() {
        const fileInput = document.getElementById('imageInput');
        const fileName = document.getElementById('fileName');
        
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        }
    }
}

// Initialize the client
const client = new OmniParserClient();
