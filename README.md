# Timelime Backend

Backend API for Timelime - an AI-powered timeline creation and quiz generation platform.

## Overview

Timelime Backend is a Flask-based REST API that powers the Timelime application. It provides functionality for creating and managing timelines, generating AI-powered content, creating quizzes, and handling user subscriptions.

### Key Features

- **Timeline Management**: Create, edit, duplicate, and manage historical timelines
- **AI-Powered Content**: Generate timelines and content using OpenAI's GPT models
- **Quiz Generation**: Create interactive quizzes based on timeline content
- **Image Generation**: Generate images using DALL-E 3
- **Payment Processing**: Stripe integration for premium subscriptions
- **Real-time Updates**: WebSocket support for live updates
- **Multi-language Support**: Built-in internationalization
- **Rate Limiting**: API rate limiting to prevent abuse
- **User Authentication**: Firebase Authentication integration

## Tech Stack

- **Framework**: Flask (Python 3.9)
- **Database**: Google Cloud Firestore
- **Authentication**: Firebase Admin SDK
- **AI/ML**: OpenAI API, LangChain
- **Payment**: Stripe
- **Email**: SendGrid
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions

## Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account with Firestore enabled
- Firebase project
- OpenAI API key
- Stripe account (for payment features)
- SendGrid account (for email features)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/QDuver/timelime-backend.git
cd timelime-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials. See [SECURITY-SETUP.md](SECURITY-SETUP.md) for detailed configuration instructions.

**Required environment variables:**
- `GCP_CREDENTIALS`: Path to Google Cloud credentials JSON or JSON string
- `OPENAI_API_KEY`: Your OpenAI API key
- `STRIPE`: Stripe secret key
- `STRIPE_WEBHOOK`: Stripe webhook secret
- `SENDGRID_API_KEY`: SendGrid API key
- `FE_URL`: Frontend URL (e.g., http://localhost:3000)
- `BUCKET`: Google Cloud Storage bucket name
- `CONTACT_EMAIL`: Contact email address
- `ADMIN_EMAIL`: Admin email address

### 5. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## Docker Deployment

### Build Docker Image

```bash
docker build -t timelime-backend .
```

### Run Container

```bash
docker run -p 5000:5000 \
  -e GCP_CREDENTIALS="$(cat path/to/credentials.json)" \
  -e OPENAI_API_KEY="your-key" \
  -e STRIPE="your-stripe-key" \
  -e STRIPE_WEBHOOK="your-webhook-secret" \
  -e SENDGRID_API_KEY="your-sendgrid-key" \
  -e FE_URL="http://localhost:3000" \
  -e BUCKET="your-bucket-name" \
  -e CONTACT_EMAIL="contact@example.com" \
  -e ADMIN_EMAIL="admin@example.com" \
  timelime-backend
```

## API Endpoints

### Authentication
- `GET /auth` - Authenticate user
- `PUT /user` - Update user profile
- `POST /contact` - Send contact message

### Timelines
- `GET /timelines` - Get all user timelines
- `GET /timeline/<id>` - Get specific timeline
- `POST /manual-timeline` - Create manual timeline
- `POST /ai-timeline` - Generate AI-powered timeline
- `PUT /timeline` - Update timeline
- `POST /duplicate-timeline` - Duplicate timeline
- `DELETE /timeline/<id>` - Delete timeline

### Events
- `GET /events/<timeline_id>` - Get timeline events
- `POST /event` - Create event
- `PUT /event` - Update event
- `DELETE /event/<id>` - Delete event

### Quizzes
- `POST /create-quiz` - Generate quiz from timeline
- `GET /get-quizzes/<timeline_id>` - Get timeline quizzes
- `POST /submit-quiz` - Submit quiz answers
- `DELETE /delete-quiz/<id>` - Delete quiz

### Payment
- `POST /create-checkout-session` - Create Stripe checkout
- `POST /cancel-premium` - Cancel premium subscription
- `POST /stripe-webhook` - Stripe webhook handler

### WebSocket Events
- Real-time updates for timeline changes
- Live collaboration features

## Project Structure

```
timelime-backend/
├── routes/              # API route handlers
│   ├── auth.py         # Authentication routes
│   ├── timelines.py    # Timeline management
│   ├── events.py       # Event management
│   ├── quizzes.py      # Quiz generation
│   ├── payment.py      # Stripe integration
│   ├── websockets.py   # WebSocket handlers
│   ├── other.py        # Miscellaneous routes
│   └── playground.py   # Development/testing routes
├── models/             # Data models
│   ├── db.py          # Firestore database wrapper
│   ├── user.py        # User model
│   └── exceptions.py  # Custom exceptions
├── utils/              # Utility functions
│   ├── timelines.py   # Timeline utilities
│   ├── events.py      # Event utilities
│   ├── quizzes.py     # Quiz generation
│   ├── images.py      # Image processing
│   ├── prompts.py     # AI prompt templates
│   ├── parsing.py     # Data parsing
│   └── decorators.py  # Custom decorators
├── clients/            # External service clients
│   ├── langchain.py   # LangChain integration
│   └── dalle.py       # DALL-E image generation
├── migrations/         # Database migrations
├── clean_schedule/     # Scheduled cleanup jobs
├── translations/       # i18n support
├── .github/workflows/  # CI/CD pipelines
├── config.py          # Application configuration
├── run.py             # Application entry point
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── .env.example       # Environment variables template
└── SECURITY-SETUP.md  # Security documentation
```

## Development

### Running Migrations

```bash
python migrations/run.py
```

### Rate Limiting

The API implements rate limiting on protected routes:
- GET requests: 20/second
- POST/PUT requests: 30-40/minute
- Batch operations: 5/minute

### Authentication

All protected routes require Firebase authentication. Include the Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase-id-token>
```

### Premium Features

Some features require a premium subscription:
- AI timeline generation
- Quiz creation
- Advanced customization options

## Deployment

### Google Cloud Run

The application automatically deploys to Google Cloud Run via GitHub Actions:

- **Pre-production**: Push to `dev` branch
- **Production**: Push to `main` branch

### Required GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

**Pre-production:**
- `GCP_CREDENTIALS_PREPROD`
- `OPENAI_API_KEY_PREPROD`
- `STRIPE_PREPROD`
- `STRIPE_WEBHOOK_PREPROD`
- `SENDGRID_API_KEY_PREPROD`

**Production:**
- `GCP_CREDENTIALS_PROD`
- `OPENAI_API_KEY_PROD`
- `STRIPE_PROD`
- `STRIPE_WEBHOOK_PROD`
- `SENDGRID_API_KEY_PROD`

**Both:**
- `CONTACT_EMAIL`
- `ADMIN_EMAIL`

See [SECURITY-SETUP.md](SECURITY-SETUP.md) for detailed deployment instructions.

## Security

This project follows security best practices:
- All secrets stored in environment variables
- API rate limiting enabled
- CORS configured
- Input validation on all endpoints
- Authentication required for sensitive operations

See [SECURITY-SETUP.md](SECURITY-SETUP.md) for detailed security information.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For questions or support, contact: [CONTACT_EMAIL]

For security issues, see [SECURITY-SETUP.md](SECURITY-SETUP.md)

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [OpenAI](https://openai.com/)
- Hosted on [Google Cloud Platform](https://cloud.google.com/)
- Payments by [Stripe](https://stripe.com/)
