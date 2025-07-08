# ManMarket-Shop

A Django-based e-commerce web application with full Docker support for development and deployment.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

Make sure Docker and Docker Compose are installed and running on your system.

---

## 🛠 Development Setup

Use `docker-compose.yml` for local development.

```bash
# Clone the repository
git clone https://github.com/AmirrezaAttary/ManMarket-Shop.git
cd core

# Build and start the containers
docker-compose up --build -d

# Run database migrations inside the backend container
docker-compose exec backend python manage.py migrate
