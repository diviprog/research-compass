"""
Resume parser utility for extracting structured data from PDF resumes.
Uses pdfplumber for text extraction and regex patterns for data extraction.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from dateutil import parser as date_parser
import pdfplumber


class ResumeParser:
    """Parser for extracting structured information from resume PDFs."""

    # Common technical skills keywords
    SKILLS_KEYWORDS = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'r', 'matlab', 'sql', 'scala', 'kotlin', 'swift', 'php',

        # ML/AI
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
        'pandas', 'numpy', 'nlp', 'computer vision', 'neural networks', 'transformers',

        # Web Development
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'html', 'css', 'tailwind', 'bootstrap',

        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',

        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',

        # Data Science
        'data analysis', 'data visualization', 'statistics', 'tableau', 'power bi',

        # Other
        'git', 'linux', 'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum'
    ]

    # Section headers to identify different parts of resume
    SECTION_HEADERS = {
        'experience': r'(?i)(experience|work history|employment|professional experience)',
        'education': r'(?i)(education|academic|qualification)',
        'skills': r'(?i)(skills|technical skills|competencies|technologies)',
        'projects': r'(?i)(projects|research|publications)',
        'summary': r'(?i)(summary|objective|profile|about)',
    }

    def __init__(self, pdf_path: str):
        """Initialize parser with PDF file path."""
        self.pdf_path = pdf_path
        self.text = ""
        self.sections = {}

    def extract_text(self) -> str:
        """Extract all text from PDF."""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text())
                self.text = "\n".join(text_parts)
            return self.text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def identify_sections(self) -> Dict[str, str]:
        """Identify different sections in the resume."""
        if not self.text:
            self.extract_text()

        lines = self.text.split('\n')
        current_section = 'header'
        section_content = {current_section: []}

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if line is a section header
            section_found = False
            for section_name, pattern in self.SECTION_HEADERS.items():
                if re.match(pattern, line_stripped):
                    current_section = section_name
                    section_content[current_section] = []
                    section_found = True
                    break

            if not section_found:
                if current_section not in section_content:
                    section_content[current_section] = []
                section_content[current_section].append(line_stripped)

        # Join lines for each section
        self.sections = {k: '\n'.join(v) for k, v in section_content.items()}
        return self.sections

    def extract_email(self) -> Optional[str]:
        """Extract email address from resume."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, self.text)
        return match.group(0) if match else None

    def extract_phone(self) -> Optional[str]:
        """Extract phone number from resume."""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, self.text)
        return match.group(0) if match else None

    def extract_skills(self) -> List[str]:
        """Extract technical skills from resume."""
        skills = []
        text_lower = self.text.lower()

        # Look for skills in the dedicated skills section first
        skills_section = self.sections.get('skills', '')
        search_text = (skills_section + '\n' + text_lower).lower()

        # Find all matching skills
        for skill in self.SKILLS_KEYWORDS:
            if skill in search_text:
                # Capitalize properly
                skills.append(skill.title() if len(skill) > 3 else skill.upper())

        # Remove duplicates and sort
        skills = sorted(list(set(skills)))
        return skills

    def extract_experiences(self) -> List[Dict[str, str]]:
        """Extract work/research experiences from resume."""
        experiences = []

        experience_section = self.sections.get('experience', '')
        if not experience_section:
            return experiences

        # Split by common delimiters (multiple newlines, bullets, etc.)
        entries = re.split(r'\n(?=\S)', experience_section)

        for entry in entries:
            if len(entry.strip()) < 20:  # Skip very short entries
                continue

            experience = self._parse_experience_entry(entry)
            if experience:
                experiences.append(experience)

        return experiences

    def _parse_experience_entry(self, entry: str) -> Optional[Dict[str, str]]:
        """Parse a single experience entry."""
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            return None

        # Try to extract dates
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|(?:19|20)\d{2}|Present)'
        dates = re.findall(date_pattern, entry, re.IGNORECASE)

        start_date = dates[0] if len(dates) > 0 else None
        end_date = dates[1] if len(dates) > 1 else "Present"

        # First line usually contains title and company
        title_line = lines[0]

        # Try to extract organization (often after "at", "@", or "|")
        org_match = re.search(r'(?:at|@|\|)\s+([^,\n]+)', title_line, re.IGNORECASE)
        organization = org_match.group(1).strip() if org_match else ""

        # Title is usually before the organization
        title = re.sub(r'(?:at|@|\|).*', '', title_line, flags=re.IGNORECASE).strip()

        # Remove dates from title if present
        title = re.sub(date_pattern, '', title, flags=re.IGNORECASE).strip()

        # Description is the rest of the entry
        description = '\n'.join(lines[1:]) if len(lines) > 1 else ""

        return {
            "title": title,
            "organization": organization or "Unknown",
            "start_date": start_date or "",
            "end_date": end_date or "",
            "description": description,
            "location": ""
        }

    def extract_education(self) -> Dict[str, Optional[str]]:
        """Extract education information."""
        education_section = self.sections.get('education', '')

        # Try to find university/college
        university_patterns = [
            r'(University of [^,\n]+)',
            r'([^,\n]+University)',
            r'([^,\n]+Institute of Technology)',
            r'([^,\n]+College)',
        ]

        university = None
        for pattern in university_patterns:
            match = re.search(pattern, education_section, re.IGNORECASE)
            if match:
                university = match.group(1).strip()
                break

        # Try to find degree/major
        degree_patterns = [
            r'(B\.?S\.?|Bachelor|Master|M\.?S\.?|Ph\.?D\.?)[^\n]*in\s+([^,\n]+)',
            r'(Computer Science|Engineering|Mathematics|Physics|Biology|Chemistry)',
        ]

        major = None
        for pattern in degree_patterns:
            match = re.search(pattern, education_section, re.IGNORECASE)
            if match:
                major = match.group(0).strip()
                break

        # Try to find GPA
        gpa_match = re.search(r'GPA:?\s*(\d\.\d+)', education_section, re.IGNORECASE)
        gpa = gpa_match.group(1) if gpa_match else None

        # Try to find graduation year
        year_match = re.search(r'(20\d{2})', education_section)
        grad_year = int(year_match.group(1)) if year_match else None

        return {
            "university": university,
            "major": major,
            "gpa": gpa,
            "graduation_year": grad_year
        }

    def parse(self) -> Dict:
        """
        Parse the entire resume and return structured data.

        Returns:
            Dictionary with parsed resume data including:
            - email, phone
            - education (university, major, gpa, graduation_year)
            - skills (list)
            - experiences (list of dicts)
            - raw_text (full text)
        """
        # Extract text
        self.extract_text()

        # Identify sections
        self.identify_sections()

        # Extract all components
        education = self.extract_education()

        parsed_data = {
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "university": education.get("university"),
            "major": education.get("major"),
            "gpa": education.get("gpa"),
            "graduation_year": education.get("graduation_year"),
            "skills": self.extract_skills(),
            "past_experiences": self.extract_experiences(),
            "publications": [],  # Could be enhanced to extract publications
            "resume_text": self.text[:5000],  # First 5000 chars as summary
        }

        return parsed_data


def parse_resume(pdf_path: str) -> Dict:
    """
    Convenience function to parse a resume PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with parsed resume data
    """
    parser = ResumeParser(pdf_path)
    return parser.parse()
