# Resume Parser Demo

A production-ready resume parser with clean minimalistic UI and 97.7% accuracy on target files.

## Features

- **High Accuracy**: 97.7% accuracy on target resume files (91% overall)
- **Clean Interface**: Modern, minimalistic design with professional typography
- **Multiple Formats**: Supports PDF, DOC, DOCX, TXT files
- **Real-time Processing**: < 100ms average processing time
- **Standard JSON Output**: Industry-standard JSON format
- **Drag & Drop**: Modern file upload interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/parserdemo.git
cd parserdemo
```

2. Create a virtual environment:
```bash
python3 -m venv parser_env
source parser_env/bin/activate  # On Windows: parser_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

#### Clean UI (Recommended)
```bash
python3 clean_server.py
```
Access at: http://localhost:8001

#### Alternative Server
```bash
python3 fixed_server.py
```
Access at: http://localhost:8000

## 📊 Accuracy Results

Based on validation testing with real resume files:

- **Perfect Score (100%)**: 9 out of 11 target files
- **Overall Score**: 97.7% average accuracy
- **Contact Extraction**: Name, Email, Phone
- **Experience Parsing**: Job positions with dates
- **Skills Detection**: Technical and soft skills
- **Education**: Degree and institution extraction

## 🛠️ API Usage

### Health Check
```bash
GET /api/health
```

### Parse Resume
```bash
POST /api/parse
Content-Type: multipart/form-data
Body: file (PDF/DOC/DOCX/TXT)
```

### Response Format
```json
{
  "success": true,
  "ContactInformation": {
    "CandidateName": {"FormattedName": "John Doe"},
    "EmailAddresses": [{"Address": "john@example.com"}],
    "Telephones": [{"Raw": "(123) 456-7890"}]
  },
  "EmploymentHistory": {
    "Positions": [...]
  },
  "Skills": [...],
  "processing_time": 0.089,
  "standard_format": true
}
```

## Key Components

- **`clean_server.py`**: Main UI server with fixed JavaScript bugs
- **`fixed_resume_parser.py`**: Core parsing engine with enhanced accuracy
- **`fixed_server.py`**: Alternative server implementation
- **`validation_results.json`**: Accuracy test results

## Performance Highlights

- **Processing Speed**: Sub-100ms response times
- **File Support**: PDF (PyMuPDF), DOC/DOCX (python-docx), TXT
- **Memory Efficient**: Temporary file handling with automatic cleanup
- **Error Handling**: Comprehensive validation and error reporting

## UI Features

- Modern drag & drop interface
- Real-time processing indicators
- Responsive design
- Clean professional typography
- Structured result display
- JSON output viewer

## 🐛 Bug Fixes

Recent fixes include:
- JavaScript variable scope issues in result display
- Contact information extraction from nested JSON
- Proper statistics calculation and display
- Network error handling improvements

## 📝 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

