# SaaS POS System - Фаза 0 (Локална версия)

Multi-tenant Point of Sale система с FastAPI backend и React frontend.

## Технологии

### Backend
- FastAPI (Python)
- PostgreSQL (Multi-tenant database)
- Redis (Caching)
- JWT Authentication
- SQLAlchemy ORM

### Frontend
- React 18
- React Router
- Axios

### Infrastructure
- Docker & Docker Compose
- Nginx (за production)

## Функционалности

### ✅ Имплементирани (Фаза 0)

- **Multi-tenant архитектура** - Пълна изолация на данните между tenants
- **Authentication** - JWT tokens с role-based access
- **Dashboard** - Статистики за продажби, продукти, клиенти
- **POS Interface** - Barcode scanning, корзина, checkout
- **Products Management** - CRUD операции, stock tracking
- **Sales History** - Преглед на продажби с детайли
- **Customers Management** - База данни с клиенти

### 🚧 За бъдещо (Фаза 1+)

- Stripe integration за subscriptions
- Email notifications
- Multi-location support
- Advanced analytics
- API documentation (Swagger)
- Unit & integration tests

## Бърз старт

### Предварителни изисквания

- Docker & Docker Compose
- (Опционално) Git

### 1. Clone проекта

```bash
git clone <repo-url>
cd Barcode1
```

### 2. Стартирай с Docker Compose

```bash
docker-compose up --build
```

Това ще стартира:
- PostgreSQL на порт 5432
- Redis на порт 6379
- Backend API на порт 8000
- Frontend на порт 3000

### 3. Отвори приложението

```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### 4. Login данни (Demo tenant)

```
Username: admin
Password: admin123
```

## Demo данни

При първо стартиране, базата се инициализира със:

- **Demo Tenant**: "Demo Store"
- **Admin User**: admin / admin123
- **10 продукта** с barcode 1001-1010
- **3 клиента** с loyalty points
- **Subscription plans** (за бъдещо използване)

## Архитектура

### Multi-tenant Database Schema

ВСИЧКИ таблици имат `tenant_id` за изолация:

```
tenants
  ├── users (служители)
  ├── products
  ├── customers
  └── sales
      └── sale_items
```

### API Endpoints

#### Authentication
- `POST /api/auth/login` - Login

#### Products
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product
- `GET /api/products/barcode/{barcode}` - Get by barcode
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

#### Sales
- `GET /api/sales` - List sales
- `GET /api/sales/{id}` - Get sale
- `POST /api/sales` - Create sale

#### Customers
- `GET /api/customers` - List customers
- `GET /api/customers/{id}` - Get customer
- `POST /api/customers` - Create customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

#### Dashboard
- `GET /api/dashboard/stats` - Get statistics

### Security

- **JWT tokens** с tenant_id и user_id
- **Role-based access control** (owner, admin, manager, cashier)
- **Password hashing** с bcrypt
- **CORS protection**
- **Multi-tenant isolation** - Всеки query се филтрира по tenant_id

## Development

### Backend развойна среда

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend развойна среда

```bash
cd frontend
npm install
npm start
```

### Database migrations (бъдещо)

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Environment Variables

Виж `.env.example` за пълен списък.

### Важни settings:

```bash
# Feature toggles
STRIPE_ENABLED=false          # Локално: false, Cloud: true
EMAIL_ENABLED=false           # Локално: false, Cloud: true
SUBSCRIPTION_CHECKS_ENABLED=false  # Локално: false, Cloud: true
```

## Project Structure

```
Barcode1/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security, dependencies
│   │   ├── db/           # Database setup
│   │   ├── models/       # SQLAlchemy models
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Pages
│   │   ├── services/     # API client, auth
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── database/
│   └── init.sql          # Database schema + seed data
├── docker-compose.yml
├── .env
└── README.md
```

## Roadmap

### Фаза 0: Локална версия ✅ (Тази имплементация)
- Multi-tenant architecture
- Basic POS functionality
- Products, Sales, Customers management
- Dashboard statistics

### Фаза 1: Cloud Deployment (1-2 седмици)
- Deploy на DigitalOcean/AWS
- Domain setup (mypos.app)
- SSL certificates
- Production database

### Фаза 2: SaaS Features (2-3 седмици)
- Stripe integration
- Subscription management
- Email notifications
- Multi-tenant registration

### Фаза 3: Advanced Features (1 месец)
- Multi-location support
- Advanced analytics
- Inventory predictions
- Mobile app (React Native)

## Troubleshooting

### Database connection error

```bash
docker-compose down
docker volume rm barcode1_postgres_data
docker-compose up --build
```

### Port already in use

```bash
# Промени портовете в docker-compose.yml
ports:
  - "5433:5432"  # PostgreSQL
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Frontend не се свързва с Backend

Провери `REACT_APP_API_URL` в frontend и CORS settings в backend.

## License

MIT

## Support

За въпроси и проблеми: [GitHub Issues]
