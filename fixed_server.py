#!/usr/bin/env python3
"""
Fixed Resume Parser Server with improved accuracy
"""

import os
import time
import tempfile
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from fixed_resume_parser import FixedResumeParser
import fitz  # PyMuPDF

app = Flask(__name__)

# Initialize the fixed parser
parser = FixedResumeParser()

def convert_to_enterprise_format(parsed_result, filename):
    """Convert our parser result to enterprise-compatible format"""

    # Generate transaction metadata
    transaction_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat()

    # Transform Skills to enterprise format
    enterprise_skills = []
    for skill in parsed_result.get('Skills', []):
        enterprise_skills.append({
            'Name': skill.get('name', ''),
            'MonthsExperience': skill.get('months_experience', 12),
            'LastUsed': skill.get('last_used', '2024'),
            'Category': skill.get('category', 'Technical Skills'),
            'Confidence': skill.get('confidence', 0.8)
        })

    # Transform Employment History to enterprise format
    enterprise_positions = []
    for position in parsed_result.get('EmploymentHistory', {}).get('Positions', []):
        enterprise_positions.append({
            'Employer': {
                'Name': position.get('Company', ''),
                'Location': {
                    'CountryCode': 'US',
                    'Municipality': position.get('Location', '').split(',')[0] if ',' in position.get('Location', '') else '',
                    'Region': position.get('Location', '').split(',')[-1].strip() if ',' in position.get('Location', '') else ''
                }
            },
            'JobTitle': position.get('JobTitle', ''),
            'StartDate': position.get('StartDate', ''),
            'EndDate': position.get('EndDate', ''),
            'IsCurrent': position.get('EndDate', '') == 'Present',
            'JobLevel': 'Professional',  # Default
            'JobCategory': 'Technology',  # Default for most resumes
            'Description': ' '.join(position.get('Description', [])) if isinstance(position.get('Description'), list) else position.get('Description', ''),
            'Achievements': []
        })

    # Transform Education to enterprise format
    enterprise_education = []
    for edu in parsed_result.get('Education', {}).get('EducationDetails', []):
        enterprise_education.append({
            'SchoolName': edu.get('School', {}).get('Name', ''),
            'SchoolType': 'University',  # Default
            'Degree': {
                'Name': edu.get('Degree', {}).get('Name', ''),
                'Type': 'bachelors' if 'bachelor' in edu.get('Degree', {}).get('Name', '').lower() else 'masters'
            },
            'StartDate': edu.get('StartDate', ''),
            'EndDate': edu.get('EndDate', ''),
            'GPA': edu.get('GPA', ''),
            'IsHighestDegree': False  # Could be enhanced
        })

    # Calculate experience metadata
    total_positions = len(enterprise_positions)
    total_months = total_positions * 24  # Rough estimate: 2 years per position

    # Build enterprise-compatible response
    enterprise_response = {
        'Info': {
            'Code': 'Success',
            'Message': 'Resume parsed successfully',
            'TransactionId': transaction_id,
            'EngineVersion': '1.0.0',
            'TransactionCost': 1,
            'ParseTime': parsed_result.get('ProcessingTime', 0)
        },
        'Value': {
            'ParsingMetadata': {
                'DocumentType': 'Resume',
                'DocumentLanguage': 'en',
                'DocumentCulture': 'en-US',
                'ParserSettings': 'Standard',
                'DocumentLastModified': current_time,
                'TimezoneFromUTC': '+00:00'
            },
            'ResumeData': {
                'ContactInformation': parsed_result.get('ContactInformation', {}),
                'PersonalAttributes': {
                    'Availability': '',
                    'SecurityClearance': '',
                    'DriversLicense': '',
                    'Nationality': '',
                    'VisaStatus': ''
                },
                'ProfessionalSummary': parsed_result.get('QualificationsSummary', ''),
                'EmploymentHistory': {
                    'ExperienceSummary': {
                        'Description': f'Professional with {total_months} months of experience across {total_positions} positions',
                        'MonthsOfWorkExperience': total_months,
                        'MonthsOfManagementExperience': 0,
                        'ExecutiveType': '',
                        'AverageMonthsPerEmployer': total_months // max(total_positions, 1),
                        'FullTimeDirectHirePredictiveIndex': 0,
                        'ManagementStory': '',
                        'CurrentManagementLevel': 'Individual Contributor',
                        'ManagementScore': 0
                    },
                    'Positions': enterprise_positions
                },
                'Education': {
                    'HighestDegree': enterprise_education[0] if enterprise_education else None,
                    'EducationDetails': enterprise_education
                },
                'SkillsData': enterprise_skills,
                'Certifications': [
                    {'Name': cert} for cert in parsed_result.get('Certifications', [])
                ],
                'Languages': [
                    {
                        'Language': 'English',
                        'LanguageCode': 'en',
                        'FoundInContext': True
                    }
                ],
                'QualificationsSummary': parsed_result.get('QualificationsSummary', ''),
                'Hobbies': [],
                'Patents': [],
                'Publications': [],
                'Associations': [],
                'SecurityCredentials': [],
                'References': []
            },
            'RedactedResumeData': None,  # Could implement PII redaction
            'Conversions': {
                'HTML': '',
                'RTF': '',
                'PDF': ''
            },
            'ParsingResponse': {
                'Code': 'Success',
                'Message': 'Parsing completed successfully'
            }
        }
    }

    return enterprise_response

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def clean_doc_text_extraction(file_path, filename):
    """Alternative .doc text extraction with multiple fallback methods"""
    try:
        # Method 1: Try docx2txt
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            if text and text.strip():
                return text
        except Exception as e:
            print(f"docx2txt failed: {e}")

        # Method 2: Enhanced olefile for old .doc format (PRIORITY METHOD)
        try:
            import olefile
            if olefile.isOleFile(file_path):
                # Enhanced binary text extraction for .doc files
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Extract readable text with improved patterns
                    import re
                    # Better regex for diverse text patterns including emails, names, phones
                    text_parts = re.findall(rb'[A-Za-z0-9\s@._()\-+]{8,}', content)
                    raw_text = b' '.join(text_parts).decode('utf-8', errors='ignore')

                    if raw_text and len(raw_text) > 100:
                        cleaned_text = clean_mixed_binary_text(raw_text)
                        print(f"✅ Successfully extracted {len(cleaned_text)} chars from {filename} using olefile")
                        return cleaned_text
                    else:
                        print(f"⚠️ olefile extraction insufficient for {filename}: {len(raw_text)} chars")
        except Exception as e:
            print(f"olefile method failed: {e}")

        # Method 3: Enhanced file processor fallback
        try:
            from enhanced_file_processor import EnhancedFileProcessor
            processor = EnhancedFileProcessor()
            raw_text = processor.extract_text_from_file(file_path)
            cleaned_text = clean_mixed_binary_text(raw_text)
            return cleaned_text
        except Exception as e:
            print(f"Enhanced processor failed: {e}")

        return f"Unable to extract text from .doc file: {filename}"

    except Exception as e:
        return f"Error reading .doc file: {str(e)}"

def clean_mixed_binary_text(raw_text):
    """Enhanced cleaning of text that has binary data mixed in"""
    import re

    # Remove binary characters and control characters
    # Keep only printable ASCII and common Unicode characters
    cleaned_lines = []

    # Pre-process to handle common .doc artifacts
    # Remove excessive whitespace and control characters
    raw_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', ' ', raw_text)
    raw_text = re.sub(r'\r+', '\n', raw_text)  # Convert \r to \n

    for line in raw_text.split('\n'):
        # Remove binary data at the start of lines
        line = re.sub(r'^[^\x20-\x7E\u00A0-\uFFFF]*', '', line)

        # Extract readable text segments
        readable_parts = re.findall(r'[\x20-\x7E\u00A0-\uFFFF]{3,}', line)

        for part in readable_parts:
            # Clean up common binary artifacts
            cleaned_part = part.strip()

            # Skip very short segments and obvious binary artifacts
            if len(cleaned_part) > 2 and not re.match(r'^[^\w\s]*$', cleaned_part):
                # Additional cleaning
                cleaned_part = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', cleaned_part)  # Remove control chars
                cleaned_part = re.sub(r'\s+', ' ', cleaned_part)  # Normalize whitespace
                cleaned_part = cleaned_part.strip()

                if cleaned_part and len(cleaned_part) > 2:
                    cleaned_lines.append(cleaned_part)

    return '\n'.join(cleaned_lines)

def extract_text_from_file(file_path, filename):
    """Extract text from various file formats"""
    try:
        if filename.lower().endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif filename.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif filename.lower().endswith('.docx') or filename.lower().endswith('.doc'):
            # Use the universal parser for .docx and .doc files
            from universal_resume_parser import UniversalResumeParser
            universal_parser = UniversalResumeParser()
            raw_text = universal_parser.extract_text_from_file(file_path, filename)

            # If .doc file extraction failed, try alternative method
            if filename.lower().endswith('.doc') and raw_text.startswith('Unable to extract text'):
                return clean_doc_text_extraction(file_path, filename)

            return raw_text
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fixed Resume Parser</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .results { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .success { color: green; } .error { color: red; }
            .section { margin: 15px 0; padding: 10px; border-left: 3px solid #007cba; }
        </style>
    </head>
    <body>
        <h1>🔧 Fixed Resume Parser</h1>
        <p>Upload a resume (PDF or TXT) to test the improved parsing accuracy</p>

        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area">
                <input type="file" name="file" accept=".pdf,.txt,.doc,.docx" required>
                <br><br>
                <button type="submit">Parse Resume</button>
            </div>
        </form>

        <div id="results"></div>

        <script>
        document.getElementById('uploadForm').onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const resultsDiv = document.getElementById('results');

            resultsDiv.innerHTML = '<p>Processing...</p>';

            fetch('/parse', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const contact = data.result.ContactInformation;
                    const education = data.result.Education.EducationDetails;
                    const experience = data.result.EmploymentHistory.Positions;
                    const skills = data.result.Skills;
                    const projects = data.result.Projects;
                    const certifications = data.result.Certifications;

                    resultsDiv.innerHTML = `
                        <div class="results">
                            <h2 class="success">✅ Parsing Results (Quality Score: ${data.result.QualityScore.toFixed(2)})</h2>

                            <div class="section">
                                <h3>Contact Information</h3>
                                <p><strong>Name:</strong> ${contact.CandidateName.FormattedName}</p>
                                <p><strong>Email:</strong> ${contact.EmailAddresses[0]?.Address || 'Not found'}</p>
                                <p><strong>Phone:</strong> ${contact.Telephones[0]?.Raw || 'Not found'}</p>
                                <p><strong>Location:</strong> ${contact.Location.Municipality}, ${contact.Location.Region}</p>
                            </div>

                            <div class="section">
                                <h3>Education (${education.length} entries)</h3>
                                ${education.map(edu => `
                                    <p><strong>${edu.Degree.Name}</strong> - ${edu.School.Name} ${edu.Dates ? `(${edu.Dates})` : ''}</p>
                                `).join('')}
                            </div>

                            <div class="section">
                                <h3>Experience (${experience.length} positions)</h3>
                                ${experience.map(exp => `
                                    <p><strong>${exp.JobTitle}</strong> at ${exp.Company} ${exp.Dates ? `(${exp.Dates})` : ''}</p>
                                    ${exp.Description.length > 0 ? `<ul>${exp.Description.map(desc => `<li>${desc.substring(0, 100)}...</li>`).join('')}</ul>` : ''}
                                `).join('')}
                            </div>

                            <div class="section">
                                <h3>Skills (${skills.length} skills)</h3>
                                <p>${skills.slice(0, 10).map(skill => skill.name).join(', ')}${skills.length > 10 ? '...' : ''}</p>
                            </div>

                            <div class="section">
                                <h3>Projects (${projects.length} projects)</h3>
                                ${projects.map(proj => `<p><strong>${proj.name}</strong></p>`).join('')}
                            </div>

                            <div class="section">
                                <h3>Certifications (${certifications.length} certifications)</h3>
                                ${certifications.map(cert => `<p>${cert.name}</p>`).join('')}
                            </div>

                            <div class="section">
                                <h3>Raw JSON Output</h3>
                                <pre style="background: white; padding: 10px; overflow: auto; max-height: 300px;">${JSON.stringify(data.result, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                }
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div class="error">❌ Network error: ${error}</div>`;
            });
        };
        </script>
    </body>
    </html>
    ''')

@app.route('/parse', methods=['POST'])
def parse_resume():
    """Parse uploaded resume file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)

            # Extract text
            text = extract_text_from_file(tmp_file.name, file.filename)

            # Clean up temp file
            os.unlink(tmp_file.name)

            if not text or text.startswith('Error'):
                return jsonify({'success': False, 'error': f'Failed to extract text: {text}'})

            # Parse with fixed parser
            start_time = time.time()
            result = parser.parse_resume(text)
            processing_time = time.time() - start_time

            # Add processing time to result
            result['ProcessingTime'] = processing_time

            # Return format expected by the frontend
            return jsonify({
                'success': True,
                'result': result
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'parser': 'fixed_resume_parser'})

if __name__ == '__main__':
    print("\n🔧 Fixed Resume Parser Server")
    print("=" * 40)
    print("🌐 Server: http://localhost:8015")
    print("🔧 Fixed parsing accuracy for:")
    print("   ✅ Education extraction")
    print("   ✅ Contact information")
    print("   ✅ Skills categorization")
    print("   ✅ Projects and certifications")
    print("=" * 40)

    app.run(debug=True, host='0.0.0.0', port=8015)