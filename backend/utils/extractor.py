import re
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Comprehensive tech skills database
SKILLS_DB = {
    'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'c++', 'c#', 'csharp', 'go', 'golang',
    'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'nosql',
    'mongodb', 'postgresql', 'mysql', 'sqlite', 'oracle', 'redis', 'cassandra', 'dynamodb',
    'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js', 'node.js', 'nodejs', 'express',
    'django', 'flask', 'fastapi', 'spring', 'spring boot', 'bootstrap', 'tailwind', 'material ui',
    'html', 'css', 'sass', 'less', 'webpack', 'vite', 'babel', 'git', 'github', 'gitlab', 'bitbucket',
    'docker', 'kubernetes', 'k8s', 'aws', 'azure', 'gcp', 'google cloud', 'firebase', 'heroku',
    'netlify', 'vercel', 'linux', 'ubuntu', 'centos', 'windows', 'bash', 'shell', 'powershell',
    'jenkins', 'circleci', 'travis', 'github actions', 'gitlab ci', 'terraform', 'ansible',
    'puppet', 'chef', 'nginx', 'apache', 'redis', 'elasticsearch', 'kafka', 'rabbitmq',
    'graphql', 'rest', 'restful', 'api', 'json', 'xml', 'yaml', 'pandas', 'numpy', 'scipy',
    'sklearn', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv', 'nltk', 'spacy',
    'huggingface', 'transformers', 'machine learning', 'deep learning', 'nlp',
    'computer vision', 'data science', 'artificial intelligence', 'ai', 'ml', 'dl',
    'statistics', 'matplotlib', 'seaborn', 'plotly', 'tableau', 'powerbi', 'excel',
    'spark', 'hadoop', 'hive', 'airflow', 'dbt', 'snowflake', 'bigquery', 'etl',
    'data warehouse', 'data lake', 'ci/cd', 'devops', 'agile', 'scrum', 'jira',
    'confluence', 'notion', 'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator',
    'blender', 'unity', 'unreal engine', 'solidity', 'ethereum', 'blockchain', 'web3',
    'smart contracts', 'microservices', 'serverless', 'lambda', 'grpc', 'protobuf',
    'oauth', 'jwt', 'sso', 'ldap', 'cybersecurity', 'penetration testing', 'encryption',
    'networking', 'tcp/ip', 'http', 'https', 'dns', 'cdn', 'load balancing'
}


def extract_info(text):
    """Extract structured information from resume text."""
    doc = nlp(text[:100000])  # Limit text length for spaCy processing
    text_lower = text.lower()

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)

    # Extract phone
    phone_patterns = [
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'(\+?\d{1,3}[-.\s]?)?\d{10}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    phones = [p for p in phones if p]

    # Extract name (first PERSON entity, usually at top)
    name = None
    for ent in doc.ents:
        if ent.label_ == 'PERSON' and len(ent.text.split()) >= 2:
            name = ent.text
            break

    # Extract skills
    found_skills = set()
    for skill in SKILLS_DB:
        if len(skill) <= 3:
            pattern = r'\b' + re.escape(skill) + r'\b'
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # Extract education
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'bs', 'ms', 'ba', 'ma',
        'b.tech', 'm.tech', 'b.e', 'm.e', 'mba', 'bsc', 'msc', 'diploma',
        'degree', 'university', 'college', 'institute', 'school'
    ]
    education = []
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in education_keywords):
            clean_line = line.strip()
            if len(clean_line) > 10 and len(clean_line) < 200:
                education.append(clean_line)

    # Extract experience snippets
    experience = []
    exp_indicators = ['experience', 'work', 'employment', 'internship', 'project']
    for line in lines:
        line_lower = line.lower()
        if any(ind in line_lower for ind in exp_indicators):
            clean = line.strip()
            if len(clean) > 15 and len(clean) < 300:
                experience.append(clean)

    return {
        'name': name,
        'email': emails[0] if emails else None,
        'phone': phones[0] if phones else None,
        'skills': sorted(list(found_skills)),
        'education': list(dict.fromkeys(education))[:5],  # Deduplicate and limit
        'experience': list(dict.fromkeys(experience))[:5],
        'word_count': len(text.split()),
        'char_count': len(text)
    }
