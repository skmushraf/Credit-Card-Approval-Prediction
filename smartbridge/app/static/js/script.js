document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    const resultIdle = document.getElementById('resultIdle');
    const resultDisplay = document.getElementById('resultDisplay');
    
    const resultTitle = document.getElementById('resultTitle');
    const resultIcon = document.getElementById('resultIcon');
    const resultBadgeContainer = document.getElementById('resultBadgeContainer');
    const resultProbText = document.getElementById('resultProbText');
    const resultMsg = document.getElementById('resultMsg');
    
    const gaugeFill = document.getElementById('gaugeFill');
    const gaugePercentage = document.getElementById('gaugePercentage');
    
    const detailApproval = document.getElementById('detailApproval');
    const detailRisk = document.getElementById('detailRisk');
    
    // Checkbox linking: Unemployed checkbox disables Years Employed
    const unemployedCheck = document.getElementById('UNEMPLOYED');
    const yearsEmployedInput = document.getElementById('YEARS_EMPLOYED');
    
    unemployedCheck.addEventListener('change', () => {
        if (unemployedCheck.checked) {
            yearsEmployedInput.value = 0;
            yearsEmployedInput.disabled = true;
        } else {
            yearsEmployedInput.disabled = false;
            yearsEmployedInput.value = 5; // default reset
        }
    });
    
    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.classList.add('btn-loading');
        submitBtn.querySelector('.btn-spinner').style.display = 'inline-block';
        
        // Collect form data
        const formData = {
            CODE_GENDER: document.getElementById('CODE_GENDER').value,
            AGE: document.getElementById('AGE').value,
            NAME_FAMILY_STATUS: document.getElementById('NAME_FAMILY_STATUS').value,
            NAME_EDUCATION_TYPE: document.getElementById('NAME_EDUCATION_TYPE').value,
            CNT_CHILDREN: document.getElementById('CNT_CHILDREN').value,
            CNT_FAM_MEMBERS: document.getElementById('CNT_FAM_MEMBERS').value,
            NAME_HOUSING_TYPE: document.getElementById('NAME_HOUSING_TYPE').value,
            AMT_INCOME_TOTAL: document.getElementById('AMT_INCOME_TOTAL').value,
            NAME_INCOME_TYPE: document.getElementById('NAME_INCOME_TYPE').value,
            OCCUPATION_TYPE: document.getElementById('OCCUPATION_TYPE').value,
            YEARS_EMPLOYED: document.getElementById('YEARS_EMPLOYED').value,
            
            // Checkbox inputs
            FLAG_OWN_CAR: document.getElementById('FLAG_OWN_CAR').checked ? 1 : 0,
            FLAG_OWN_REALTY: document.getElementById('FLAG_OWN_REALTY').checked ? 1 : 0,
            UNEMPLOYED: unemployedCheck.checked ? 1 : 0,
            FLAG_WORK_PHONE: document.getElementById('FLAG_WORK_PHONE').checked ? 1 : 0,
            FLAG_PHONE: document.getElementById('FLAG_PHONE').checked ? 1 : 0,
            FLAG_EMAIL: document.getElementById('FLAG_EMAIL').checked ? 1 : 0
        };
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                renderResult(result);
            } else {
                alert(`Error: ${result.message}`);
            }
            
        } catch (error) {
            console.error('Prediction request failed:', error);
            alert('Server error occurred during evaluation. Please try again.');
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
            submitBtn.querySelector('.btn-spinner').style.display = 'none';
        }
    });
    
    // Reset page layout
    resetBtn.addEventListener('click', () => {
        resultDisplay.classList.add('hidden');
        resultIdle.classList.remove('hidden');
        form.reset();
        yearsEmployedInput.disabled = false;
    });
    
    function renderResult(data) {
        // Hide idle view, display result view
        resultIdle.classList.add('hidden');
        resultDisplay.classList.remove('hidden');
        
        const isApproved = data.prediction === 0;
        
        // Update labels
        resultTitle.textContent = data.status_label;
        resultMsg.textContent = data.message;
        
        // Reset classes
        resultTitle.className = '';
        resultBadgeContainer.className = 'result-badge-container';
        resultIcon.className = 'fa-solid';
        
        const approvalRate = data.approval_rate;
        
        // Configure approved vs rejected styles
        if (isApproved) {
            resultTitle.classList.add('text-success');
            resultBadgeContainer.classList.add('badge-approved');
            resultIcon.classList.add('fa-circle-check');
            resultProbText.textContent = `Approval Confidence: ${approvalRate}%`;
            
            detailApproval.textContent = `${approvalRate}%`;
            detailApproval.className = 'val text-success';
            detailRisk.textContent = 'Low';
            detailRisk.className = 'val text-success';
            
            gaugeFill.style.stroke = 'var(--success)';
        } else {
            resultTitle.classList.add('text-danger');
            resultBadgeContainer.classList.add('badge-rejected');
            resultIcon.classList.add('fa-circle-xmark');
            resultProbText.textContent = `Risk Probability: ${data.rejection_rate}%`;
            
            detailApproval.textContent = `${approvalRate}%`;
            detailApproval.className = 'val text-danger';
            detailRisk.textContent = 'High';
            detailRisk.className = 'val text-danger';
            
            gaugeFill.style.stroke = 'var(--danger)';
        }
        
        // Animate circular progress gauge
        // Circumference = 2 * pi * r = 2 * 3.14159 * 40 = 251.2
        const circumference = 251.2;
        // Gauge displays approval rate
        const fillPercent = isApproved ? approvalRate : (100 - data.rejection_rate);
        const offset = circumference - (fillPercent / 100) * circumference;
        
        // Apply offset trigger after rendering
        setTimeout(() => {
            gaugeFill.style.strokeDashoffset = offset;
            gaugePercentage.textContent = `${Math.round(fillPercent)}%`;
        }, 100);
    }
});
