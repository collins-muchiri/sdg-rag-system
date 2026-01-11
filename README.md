# SDG RAG System - Quick Start Guide

## 🚀 Project Overview

This is a comprehensive RAG (Retrieval-Augmented Generation) based system for UN/UN Habitat SDG file management and searching. The system automatically processes documents, classifies them by Sustainable Development Goals, and provides intelligent search capabilities with real-time transportation data integration.

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (for caching and background tasks)
- 8GB+ RAM recommended
- Internet connection for API calls

## 🛠️ Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd "C:\Users\Unsub_Log\OneDrive\Desktop\Project Vault\RAG BASED SYSTEM"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL if not already installed
# Windows: Download from postgresql.org
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql postgresql-contrib

# Create database
createdb sdg_rag_db

# Install pgvector extension (run in psql)
psql -d sdg_rag_db -c "CREATE EXTENSION vector;"
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys:
# - OPENAI_API_KEY (required)
# - ANTHROPIC_API_KEY (optional)
# - TFL_API_KEY (for London transit data)
# - OPEN_CHARGE_MAP_API_KEY (for EV charging stations)
# - UBER_API_KEY (for ride-sharing data)
# - DATABASE_URL (PostgreSQL connection string)
```

### 4. Start the System

```bash
# Start the API server
python main.py

# The system will be available at:
# http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## 🎯 Key Features

### 1. Document Processing
- **Upload**: PDF, DOCX, TXT, MD, PPTX files
- **AI Classification**: Automatic SDG goal classification
- **Text Extraction**: Advanced document parsing
- **Vector Storage**: Semantic search capabilities

### 2. Intelligent Search
- **Semantic Search**: Find documents by meaning, not just keywords
- **SDG Filtering**: Search by specific Sustainable Development Goals
- **Similar Documents**: Find related content automatically

### 3. Real-time Transportation Data
- **Public Transit**: London TfL, and other city transit systems
- **EV Infrastructure**: Electric vehicle charging stations
- **Aviation Data**: Flight information and airport status
- **Maritime Data**: Vessel tracking and port information
- **Ride-sharing**: Uber and other mobility services

### 4. SDG Monitoring
- **Goal Classification**: AI-powered SDG categorization
- **Cross-reference Analysis**: Find connections between goals
- **Progress Tracking**: Monitor SDG-related activities
- **Dashboard Views**: Comprehensive overview interfaces

## 📚 API Endpoints

### Documents
- `POST /api/v1/documents/upload` - Upload and process documents
- `GET /api/v1/documents/{document_id}` - Get document information
- `DELETE /api/v1/documents/{document_id}` - Delete documents

### Search
- `GET /api/v1/search/` - Search documents with RAG
- `GET /api/v1/search/semantic` - Advanced semantic search
- `GET /api/v1/search/classify` - Classify queries by SDG

### SDG Management
- `GET /api/v1/sdg/goals` - Get all SDG goals
- `GET /api/v1/sdg/goals/{goal_id}/documents` - Get documents by SDG
- `GET /api/v1/sdg/goals/overview` - SDG overview dashboard

### Transportation Data
- `GET /api/v1/transportation/transit/london` - London transit data
- `GET /api/v1/transportation/ev/charging-stations` - EV charging stations
- `GET /api/v1/transportation/dashboard` - Transportation dashboard

## 🔧 Usage Examples

### Upload and Classify a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### Search for SDG-related Documents

```bash
curl "http://localhost:8000/api/v1/search/?q=climate+action&sdg_goal=13&limit=10"
```

### Get EV Charging Stations

```bash
curl "http://localhost:8000/api/v1/transportation/ev/charging-stations?latitude=51.5074&longitude=-0.1278&radius=10"
```

## 🌍 Integration with External APIs

The system integrates with numerous transportation APIs from the public-apis repository:

### High-Priority APIs for SDG Monitoring:
1. **Open Charge Map** - EV infrastructure (SDG 7, 11, 13)
2. **Transport for London** - Urban mobility (SDG 11)
3. **TransitLand** - Global transit aggregation (SDG 11)
4. **ADS-B Exchange** - Aviation monitoring (SDG 9, 11)
5. **Smartcar** - Vehicle telematics (SDG 11, 13)

### Configuration Required:
- Add API keys to `.env` file
- Enable specific endpoints in configuration
- Monitor rate limits and usage quotas

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI       │    │   AI Models     │
│   (React)       │◄──►│   Backend       │◄──►│   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vector DB     │    │   PostgreSQL     │    │   External APIs │
│   (ChromaDB)    │    │   (Metadata)     │    │   (Transport)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 Security Considerations

- **API Keys**: Store securely in environment variables
- **Data Privacy**: Automatic PII removal from documents
- **Access Control**: Role-based permissions (configurable)
- **Rate Limiting**: Built-in API rate limiting
- **Encryption**: AES-256 for sensitive data

## 🚦 Monitoring and Maintenance

### Health Checks
- `GET /health` - System health status
- `GET /` - API status and version

### Logging
- Structured JSON logging
- Error tracking and alerting
- Performance metrics

### Scaling
- Horizontal scaling with load balancers
- Vector database sharding
- API gateway for high availability

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📞 Support

For issues and questions:
- Check API documentation at `/docs`
- Review logs for error details
- Verify API key configurations
- Check database connectivity

## 🎯 Next Steps

1. **Setup**: Complete installation and configuration
2. **Test**: Upload sample documents and test search
3. **Integrate**: Add transportation API keys
4. **Customize**: Adjust SDG classification prompts
5. **Deploy**: Scale for production use

This system provides a comprehensive foundation for UN/UN Habitat SDG document management with real-time data integration and AI-powered search capabilities.