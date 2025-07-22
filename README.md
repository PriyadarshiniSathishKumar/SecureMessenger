## SecureChat - Encrypted Messaging System
# Overview
SecureChat is a secure, end-to-end encrypted messaging application built with Flask. The system provides real-time chat functionality with military-grade Fernet encryption, ensuring all messages are encrypted before storage and transmission. Users can create accounts, join chat rooms, and exchange encrypted messages in a secure environment.

# User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
# Frontend Architecture
Template Engine: Jinja2 templates with Bootstrap-based responsive UI
Styling: Bootstrap 5 with dark theme support and custom CSS
JavaScript: Vanilla JavaScript for chat functionality and real-time updates
UI Components: Modern dark theme with Feather icons for visual elements

# Backend Architecture
Framework: Flask (Python web framework)
Database ORM: SQLAlchemy with Flask-SQLAlchemy extension
Authentication: Flask-Login for session management
Security: Werkzeug for password hashing, custom encryption layer
Architecture Pattern: Blueprint-based modular structure

## Database Design
Primary Database: SQLite (development) with PostgreSQL support (production)
Models: User, Room, Message, RoomMember entities
Relationships: Many-to-many user-room relationships, one-to-many message relationships

## Key Components
# Authentication System
User registration and login with password hashing (Werkzeug)
Session-based authentication using Flask-Login
Password strength validation (minimum 6 characters)
Remember me functionality for persistent sessions

# Encryption Layer (CryptoManager)
Algorithm: Fernet symmetric encryption (AES 128 in CBC mode with HMAC)
Key Management: Master key stored in file system or environment variables
Message Encryption: All messages encrypted before database storage
Key Rotation: Supports master key regeneration and fallback mechanisms
Chat Room System

## Room creation and management
# User membership management
Private and public room support
Real-time message loading and display
Message Handling
Encrypted message storage
Real-time message retrieval via AJAX polling
Message decryption on display
Auto-scrolling chat interface

## Data Flow
# Message Sending Flow
User submits message through web form
Message text encrypted using CryptoManager
Encrypted message stored in database with metadata
Client receives confirmation and updates UI
Other users retrieve encrypted messages via polling
Messages decrypted on client display

## Authentication Flow
User provides credentials via login form
Password verified against stored hash
Flask-Login creates session and manages user state
Protected routes require authentication decorators
Session persists across requests until logout

## Room Management Flow
Users can create new rooms or join existing ones
Room membership tracked in RoomMember junction table
Messages filtered by room membership
Real-time updates show latest messages per room

## External Dependencies
Core Framework Dependencies
Flask: Web application framework
SQLAlchemy: Database ORM and connection management
Flask-Login: User session and authentication management
Flask-SQLAlchemy: Flask integration for SQLAlchemy
Cryptography Dependencies
cryptography: Provides Fernet cipher implementation
Werkzeug: Password hashing and security utilities

## Frontend Dependencies
Bootstrap 5: CSS framework with dark theme support
Feather Icons: SVG icon library for UI elements
Custom CSS/JS: Application-specific styling and functionality
Infrastructure Dependencies
ProxyFix: WSGI middleware for deployment behind reverse proxies
Environment Variables: Configuration management for secrets and database URLs
Deployment Strategy

## Environment Configuration
Development: SQLite database, debug mode enabled, file-based key storage
Production: PostgreSQL via DATABASE_URL environment variable
Security: Master encryption key via MASTER_ENCRYPTION_KEY environment variable
Session Security: SESSION_SECRET environment variable for session encryption

## Key Security Considerations
All sensitive data encrypted at rest using Fernet cipher
Password hashing using industry-standard Werkzeug implementation
HTTPS enforcement through ProxyFix middleware
Environment-based configuration prevents secrets in code
## Database Migration Strategy
SQLAlchemy handles table creation automatically via create_all()
Model changes require manual migration planning
Support for both SQLite (development) and PostgreSQL (production)

## Scalability Considerations
Database connection pooling with recycle and pre-ping options
Session-based architecture suitable for load balancing
Encryption keys managed centrally for horizontal scaling

# Working video - https://drive.google.com/file/d/1gGuDObF4aRUY95x6mudt1ic1hI2GnKDi/view?usp=sharing
## Screenshots 
<img width="1919" height="867" alt="Screenshot 2025-07-22 181344" src="https://github.com/user-attachments/assets/5897162f-6843-40f0-8a54-ba8d3b2435e6" />
<img width="1919" height="867" alt="Screenshot 2025-07-22 181350" src="https://github.com/user-attachments/assets/57f0f59d-9c4a-4ca1-b010-9876bdf3c5c5" />
<img width="1919" height="869" alt="Screenshot 2025-07-22 181401" src="https://github.com/user-attachments/assets/9ca89638-f681-426f-ab76-d679a5629a49" />
<img width="1919" height="856" alt="Screenshot 2025-07-22 181458" src="https://github.com/user-attachments/assets/bb89adfd-fba9-4cb1-ae25-b7a213c58038" />
<img width="1919" height="864" alt="Screenshot 2025-07-22 181508" src="https://github.com/user-attachments/assets/6ebf7427-66ba-4ce7-8dae-ee1c78b44dfb" />





