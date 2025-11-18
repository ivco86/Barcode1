from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.db.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.customer import Customer
from app.core.dependencies import get_current_user, check_subscription
from app.api.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    check_subscription(current_user["tenant_id"], db)

    today = date.today()
    tenant_id = current_user["tenant_id"]

    # Total sales today
    today_sales = db.query(
        func.coalesce(func.sum(Sale.total), 0),
        func.count(Sale.id)
    ).filter(
        Sale.tenant_id == tenant_id,
        func.date(Sale.created_at) == today
    ).first()

    total_sales_today = float(today_sales[0] or 0)
    total_sales_count_today = today_sales[1] or 0

    # Total products
    total_products = db.query(func.count(Product.id)).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True
    ).scalar()

    # Low stock products
    low_stock_products = db.query(func.count(Product.id)).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.stock <= Product.min_stock
    ).scalar()

    # Total customers
    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.tenant_id == tenant_id
    ).scalar()

    # Revenue last 7 days
    revenue_last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily_revenue = db.query(
            func.coalesce(func.sum(Sale.total), 0)
        ).filter(
            Sale.tenant_id == tenant_id,
            func.date(Sale.created_at) == day
        ).scalar()

        revenue_last_7_days.append({
            "date": day.isoformat(),
            "revenue": float(daily_revenue or 0)
        })

    return {
        "total_sales_today": total_sales_today,
        "total_sales_count_today": total_sales_count_today,
        "total_products": total_products or 0,
        "low_stock_products": low_stock_products or 0,
        "total_customers": total_customers or 0,
        "revenue_last_7_days": revenue_last_7_days
    }
