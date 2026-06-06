import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def analyze_resume(text, info, job_description=''):
    """Analyze resume and generate ATS score and feedback."""
    word_count = info.get('word_count', 0)
    skills = info.get('skills', [])
    text_lower = text.lower()

    score = 0
    suggestions = []
    strengths = []

    # 1. Resume Length (20 points) — Ideal: 300-650 words
    if 300 <= word_count <= 650:
        score += 20
        strengths.append("Optimal resume length for ATS systems")
    elif word_count < 250:
        score += max(2, word_count // 50)
        suggestions.append("Resume is too short. Aim for 300-650 words to fully showcase your experience.")
    elif word_count > 800:
        score += max(10, 20 - (word_count - 650) // 50)
        suggestions.append("Resume is quite long. Consider condensing to 1-2 pages for better ATS performance.")
    else:
        score += 15

    # 2. Skills Diversity (25 points)
    skills_count = len(skills)
    if skills_count >= 12:
        score += 25
        strengths.append(f"Excellent technical skills coverage ({skills_count} skills detected)")
    elif skills_count >= 6:
        score += 15 + (skills_count - 6)
        strengths.append(f"Good technical skills coverage ({skills_count} skills detected)")
    else:
        score += max(2, skills_count * 2)
        suggestions.append(f"Only {skills_count} technical skills detected. Add more relevant skills from the job domain.")

    # 3. Contact Information (15 points)
    contact_score = 0
    if info.get('email'):
        contact_score += 5
    else:
        suggestions.append("Add a professional email address at the top of your resume.")

    if info.get('phone'):
        contact_score += 5
    else:
        suggestions.append("Add a phone number for recruiters to contact you.")

    if info.get('name'):
        contact_score += 5
    else:
        suggestions.append("Ensure your full name is clearly visible at the top.")

    score += contact_score
    if contact_score == 15:
        strengths.append("Complete contact information provided")

    # 4. Section Completeness (20 points)
    sections = {
        'Education': ['education', 'academic', 'degree', 'university', 'college', 'qualification'],
        'Experience': ['experience', 'work', 'employment', 'internship', 'career', 'professional'],
        'Skills': ['skills', 'technologies', 'tools', 'expertise', 'proficiencies', 'technical'],
        'Projects': ['project', 'portfolio', 'github'],
        'Summary': ['summary', 'objective', 'profile', 'about', 'overview']
    }

    found_sections = 0
    missing_sections = []
    for section, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            found_sections += 1
        else:
            missing_sections.append(section)

    section_score = (found_sections / len(sections)) * 20
    score += section_score

    if found_sections >= 4:
        strengths.append("Well-structured with clear sections")
    if missing_sections:
        suggestions.append(f"Consider adding these sections: {', '.join(missing_sections)}")

    # 5. Formatting & Readability (10 points)
    format_score = 10

    # Check for excessive special characters (possible tables/graphics)
    special_chars = len(re.findall(r'[^\w\s.,;:\-@()/]', text))
    if special_chars > 100:
        format_score -= 4
        suggestions.append("Excessive special characters detected. Avoid complex tables or graphics that confuse ATS.")

    # Check for consistent line breaks
    if text.count('\n\n\n') > 15:
        format_score -= 2
        suggestions.append("Inconsistent spacing detected. Use uniform spacing between sections.")

    # Check for very long lines (possible columns)
    long_lines = [line for line in text.split('\n') if len(line) > 150]
    if len(long_lines) > 10:
        format_score -= 2
        suggestions.append("Very long lines detected. Avoid multi-column layouts for better ATS parsing.")

    score += max(0, format_score)

    # 6. Job Description Match (10 points bonus)
    jd_match_score = None
    if job_description and len(job_description) > 50:
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            tfidf_matrix = vectorizer.fit_transform([text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            jd_match_score = round(similarity * 100, 1)
            score += (similarity * 10)

            # Find missing keywords
            jd_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_description.lower()))
            resume_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', text_lower))
            missing_keywords = [w for w in jd_words if w not in resume_words]
            if missing_keywords:
                top_missing = missing_keywords[:5]
                suggestions.append(f"Keywords from job description missing: {', '.join(top_missing)}")

        except Exception:
            pass

    # 7. Action Verbs & Impact (10 points)
    action_verbs = [
        'developed', 'designed', 'implemented', 'created', 'built', 'engineered', 'architected',
        'optimized', 'improved', 'enhanced', 'reduced', 'increased', 'decreased', 'automated',
        'deployed', 'maintained', 'tested', 'debugged', 'resolved', 'led', 'managed',
        'coordinated', 'collaborated', 'initiated', 'streamlined', 'transformed', 'accelerated',
        'delivered', 'launched', 'spearheaded', 'drove', 'negotiated', 'achieved', 'won'
    ]
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)

    if verb_count >= 8:
        score += 10
        strengths.append(f"Strong use of action verbs ({verb_count} detected)")
    elif verb_count >= 4:
        score += 6
        strengths.append(f"Good use of action verbs ({verb_count} detected)")
    else:
        suggestions.append("Use more action verbs (developed, implemented, optimized, led) to describe achievements.")

    # 8. Quantifiable achievements bonus
    numbers = re.findall(r'\d+%|\d+\s*(million|thousand|k|m|users|customers|dollars|usd)?', text_lower)
    if len(numbers) >= 3:
        score += 5
        strengths.append("Good use of quantifiable achievements (numbers/metrics)")

    # Final score
    final_score = min(100, max(0, round(score)))

    # Determine rating
    if final_score >= 85:
        rating = "Excellent"
        rating_color = "#22c55e"
    elif final_score >= 70:
        rating = "Good"
        rating_color = "#f97316"
    elif final_score >= 50:
        rating = "Average"
        rating_color = "#eab308"
    else:
        rating = "Needs Improvement"
        rating_color = "#ef4444"

    # Categorize skills
    skill_categories = categorize_skills(skills)

    return {
        'ats_score': final_score,
        'rating': rating,
        'rating_color': rating_color,
        'word_count': word_count,
        'skills_count': skills_count,
        'sections_found': found_sections,
        'total_sections': len(sections),
        'contact_complete': contact_score == 15,
        'jd_match_score': jd_match_score,
        'action_verbs_count': verb_count,
        'quantifiable_metrics': len(numbers),
        'suggestions': suggestions,
        'strengths': strengths,
        'skill_categories': skill_categories
    }


def categorize_skills(skills):
    """Categorize skills into domains."""
    categories = {
        'Programming Languages': [
            'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'c++', 'c#', 'csharp',
            'go', 'golang', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
            'sql', 'html', 'css', 'sass', 'less', 'shell', 'bash', 'powershell'
        ],
        'Frameworks & Libraries': [
            'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js', 'node.js', 'nodejs',
            'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'bootstrap',
            'tailwind', 'material ui', 'webpack', 'vite', 'babel', 'pandas', 'numpy', 'scipy',
            'sklearn', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv', 'nltk',
            'spacy', 'huggingface', 'transformers', 'matplotlib', 'seaborn', 'plotly'
        ],
        'Databases & Storage': [
            'mongodb', 'postgresql', 'mysql', 'sqlite', 'oracle', 'redis', 'cassandra',
            'dynamodb', 'elasticsearch', 'snowflake', 'bigquery', 'firebase'
        ],
        'Cloud & DevOps': [
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins',
            'circleci', 'travis', 'github actions', 'gitlab ci', 'terraform', 'ansible',
            'puppet', 'chef', 'heroku', 'netlify', 'vercel', 'lambda', 'serverless',
            'ci/cd', 'nginx', 'apache'
        ],
        'AI & Data Science': [
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
            'artificial intelligence', 'ai', 'ml', 'dl', 'statistics', 'etl', 'data warehouse',
            'data lake', 'spark', 'hadoop', 'hive', 'airflow', 'dbt'
        ],
        'Tools & Platforms': [
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'notion', 'figma',
            'sketch', 'adobe xd', 'photoshop', 'illustrator', 'tableau', 'powerbi', 'excel',
            'blender', 'unity', 'unreal engine'
        ],
        'Web3 & Blockchain': [
            'solidity', 'ethereum', 'blockchain', 'web3', 'smart contracts'
        ],
        'Security & Networking': [
            'cybersecurity', 'penetration testing', 'encryption', 'networking', 'tcp/ip',
            'http', 'https', 'dns', 'cdn', 'load balancing', 'oauth', 'jwt', 'sso', 'ldap'
        ]
    }

    result = {}
    for skill in skills:
        assigned = False
        for cat, cat_skills in categories.items():
            if skill in cat_skills:
                result.setdefault(cat, []).append(skill)
                assigned = True
                break
        if not assigned:
            result.setdefault('Other Skills', []).append(skill)

    return result
