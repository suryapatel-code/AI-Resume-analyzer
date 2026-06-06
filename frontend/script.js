const API_URL = 'http://localhost:5000/api'; // Change this to your deployed backend URL

const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const jobDesc = document.getElementById('jobDesc');

let selectedFile = null;

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
        alert('Please upload a PDF or DOCX file');
        return;
    }
    
    selectedFile = file;
    fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    analyzeBtn.disabled = false;
}

analyzeBtn.addEventListener('click', analyzeResume);

async function analyzeResume() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('resume', selectedFile);
    if (jobDesc.value.trim()) {
        formData.append('job_description', jobDesc.value.trim());
    }

    loading.classList.add('active');
    results.classList.remove('active');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed to analyze resume. Make sure the backend is running.');
        console.error(error);
    } finally {
        loading.classList.remove('active');
        analyzeBtn.disabled = false;
    }
}

function displayResults(data) {
    const { extracted_info, analysis } = data;
    
    results.classList.add('active');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Score animation
    animateScore(analysis.ats_score, analysis.rating, analysis.rating_color);
    
    // Stats
    document.getElementById('wordCount').textContent = analysis.word_count;
    document.getElementById('skillsCount').textContent = analysis.skills_count;
    document.getElementById('sectionsCount').textContent = `${analysis.sections_found}/${analysis.total_sections}`;
    document.getElementById('verbsCount').textContent = analysis.action_verbs_count;

    // JD Match
    const jdSection = document.getElementById('jdMatchSection');
    if (analysis.jd_match_score !== null) {
        jdSection.classList.add('active');
        document.getElementById('jdMatchFill').style.width = `${analysis.jd_match_score}%`;
        document.getElementById('jdMatchText').textContent = `${analysis.jd_match_score}% match with job description`;
    } else {
        jdSection.classList.remove('active');
    }

    // Extracted Info
    document.getElementById('infoName').textContent = extracted_info.name || 'Not detected';
    document.getElementById('infoEmail').textContent = extracted_info.email || 'Not detected';
    document.getElementById('infoPhone').textContent = extracted_info.phone || 'Not detected';

    // Education
    const eduList = document.getElementById('educationList');
    eduList.innerHTML = '';
    if (extracted_info.education && extracted_info.education.length > 0) {
        extracted_info.education.forEach(edu => {
            const li = document.createElement('li');
            li.textContent = edu;
            eduList.appendChild(li);
        });
    } else {
        eduList.innerHTML = '<li style="color: rgba(255,255,255,0.5)">No education details detected</li>';
    }

    // Skills
    const skillsContainer = document.getElementById('skillsContainer');
    skillsContainer.innerHTML = '';
    
    if (Object.keys(analysis.skill_categories).length > 0) {
        for (const [category, skills] of Object.entries(analysis.skill_categories)) {
            if (skills.length === 0) continue;
            
            const div = document.createElement('div');
            div.className = 'skill-category';
            
            const name = document.createElement('span');
            name.className = 'skill-category-name';
            name.textContent = category;
            div.appendChild(name);
            
            skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                div.appendChild(tag);
            });
            
            skillsContainer.appendChild(div);
        }
    } else {
        skillsContainer.innerHTML = '<p style="color: rgba(255,255,255,0.5)">No skills detected. Try adding a skills section.</p>';
    }

    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    if (analysis.strengths && analysis.strengths.length > 0) {
        analysis.strengths.forEach(s => {
            if (s) {
                const li = document.createElement('li');
                li.textContent = s;
                strengthsList.appendChild(li);
            }
        });
    } else {
        strengthsList.innerHTML = '<li>No major strengths detected yet</li>';
    }

    // Suggestions
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    if (analysis.suggestions && analysis.suggestions.length > 0) {
        analysis.suggestions.forEach(s => {
            const li = document.createElement('li');
            li.textContent = s;
            suggestionsList.appendChild(li);
        });
    } else {
        suggestionsList.innerHTML = '<li>Great job! No major suggestions at this time.</li>';
    }
}

function animateScore(targetScore, rating, color) {
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const ratingText = document.getElementById('ratingText');
    const scoreSummary = document.getElementById('scoreSummary');

    // Animate number
    let current = 0;
    const increment = targetScore / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
            current = targetScore;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(current);
    }, 20);

    // Animate circle
    const circumference = 100;
    const offset = circumference - (targetScore / 100) * circumference;
    setTimeout(() => {
        scoreCircle.style.strokeDasharray = `${targetScore}, 100`;
    }, 100);

    // Update text
    ratingText.textContent = rating;
    ratingText.style.color = color;
    
    if (targetScore >= 80) {
        scoreSummary.textContent = "Your resume is well-optimized and ATS-friendly!";
    } else if (targetScore >= 60) {
        scoreSummary.textContent = "Good foundation, but there's room for improvement.";
    } else {
        scoreSummary.textContent = "Your resume needs significant improvements for ATS systems.";
    }
}
