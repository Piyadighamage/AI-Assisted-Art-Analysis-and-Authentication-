// Main JavaScript for Art Analysis Platform

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadContent = document.getElementById('uploadContent');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));

    let selectedFile = null;

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Upload area click handler
    uploadArea.addEventListener('click', function() {
        if (!previewContainer.classList.contains('d-none')) return;
        fileInput.click();
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Button handlers
    analyzeBtn.addEventListener('click', analyzeImage);
    changeImageBtn.addEventListener('click', function() {
        resetUploadArea();
        fileInput.click();
    });

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            processFile(file);
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }

    function processFile(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please select a valid image file (JPG, PNG, GIF, BMP)', 'error');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            showAlert('File size must be less than 16MB', 'error');
            return;
        }

        selectedFile = file;
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            showPreview();
        };
        reader.readAsDataURL(file);
    }

    function showPreview() {
        uploadContent.classList.add('d-none');
        previewContainer.classList.remove('d-none');
        previewContainer.classList.add('fade-in');
    }

    function resetUploadArea() {
        uploadContent.classList.remove('d-none');
        previewContainer.classList.add('d-none');
        previewContainer.classList.remove('fade-in');
        selectedFile = null;
        fileInput.value = '';
    }

    function analyzeImage() {
        if (!selectedFile) {
            showAlert('Please select an image first', 'error');
            return;
        }

        // Show loading modal
        loadingModal.show();

        // Create form data
        const formData = new FormData();
        formData.append('artwork', selectedFile);

        // Send to server
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.hide();
            
            if (data.error) {
                showAlert(data.error, 'error');
            } else {
                showResults(data);
            }
        })
        .catch(error => {
            loadingModal.hide();
            console.error('Error:', error);
            showAlert('An error occurred during analysis. Please try again.', 'error');
        });
    }

    function showResults(data) {
        console.log('Showing results:', data); // Debug log
        
        const resultsContent = document.getElementById('resultsContent');
        
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <img src="${data.image_url}" class="img-fluid rounded" alt="Analyzed artwork">
                </div>
                <div class="col-md-6">
                    <h5 class="mb-3">Analysis Results</h5>
        `;

        // Authenticity Results
        if (data.authenticity && !data.authenticity.error) {
            const isHuman = data.authenticity.is_human;
            const badgeClass = isHuman ? 'human' : 'ai';
            // Convert numpy float to regular number if needed
            const confidence = typeof data.authenticity.confidence === 'object' 
                ? parseFloat(data.authenticity.confidence) 
                : data.authenticity.confidence;
            
            html += `
                <div class="result-card">
                    <h6>Authenticity Assessment</h6>
                    <div class="authenticity-badge ${badgeClass}">
                        ${data.authenticity.prediction}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Confidence:</span>
                        <strong>${confidence.toFixed(2)}%</strong>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                </div>
            `;
        } else if (data.authenticity && data.authenticity.error) {
            html += `
                <div class="alert alert-warning">
                    <h6>Authenticity Analysis</h6>
                    <p class="mb-0">Error: ${data.authenticity.error}</p>
                </div>
            `;
        }

        // Style Results
        if (data.style && !data.style.error) {
            // Convert numpy float to regular number if needed
            const confidence = typeof data.style.confidence === 'object' 
                ? parseFloat(data.style.confidence) 
                : data.style.confidence;
                
            html += `
                <div class="result-card">
                    <h6>Style Classification</h6>
                    <div class="style-prediction">
                        <strong>${data.style.predicted_style}</strong>
                        <div class="d-flex justify-content-between align-items-center mt-2">
                            <span>Confidence:</span>
                            <strong>${confidence.toFixed(2)}%</strong>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidence}%"></div>
                        </div>
                    </div>
            `;

            if (data.style.top_3_predictions && data.style.top_3_predictions.length > 1) {
                html += `
                    <div class="mt-3">
                        <small class="text-muted">Alternative predictions:</small>
                `;
                
                data.style.top_3_predictions.slice(1).forEach(pred => {
                    const predConfidence = typeof pred.confidence === 'object' 
                        ? parseFloat(pred.confidence) 
                        : pred.confidence;
                    html += `
                        <div class="d-flex justify-content-between mt-1">
                            <span>${pred.style}</span>
                            <span>${predConfidence.toFixed(2)}%</span>
                        </div>
                    `;
                });
                
                html += `</div>`;
            }

            html += `</div>`;
        } else if (data.style && data.style.error) {
            html += `
                <div class="alert alert-warning">
                    <h6>Style Analysis</h6>
                    <p class="mb-0">Error: ${data.style.error}</p>
                </div>
            `;
        }

        // General error
        if (data.error) {
            html += `
                <div class="alert alert-danger">
                    <h6>Analysis Error</h6>
                    <p class="mb-0">${data.error}</p>
                </div>
            `;
        }

        html += `
                </div>
            </div>
        `;

        resultsContent.innerHTML = html;
        resultsModal.show();

        // Animate confidence bars after modal is shown
        setTimeout(() => {
            document.querySelectorAll('.confidence-fill').forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            });
        }, 500);
    }

    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Smooth scrolling for anchor links
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

    // Add loading animation to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.id === 'analyzeBtn') return; // Skip for analyze button as it has custom handling
            
            const originalText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            setTimeout(() => {
                this.disabled = false;
                this.innerHTML = originalText;
            }, 2000);
        });
    });
});