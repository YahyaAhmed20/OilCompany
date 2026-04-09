from django.shortcuts import render
from django.db.models import Sum
from decimal import Decimal

from .models import (
    Supplier,
    SupplierTransaction,
    Customer,
    CustomerTransaction,
    StearinReservation
)


def dashboard(request):

    # ======================
    # الموردين
    # ======================
    suppliers_count = Supplier.objects.count()

    total_supplier_balance = SupplierTransaction.objects.aggregate(
        total=Sum('balance')
    )['total'] or Decimal('0.00')

    total_debit = SupplierTransaction.objects.aggregate(
        total=Sum('debit')
    )['total'] or Decimal('0.00')

    total_credit = SupplierTransaction.objects.aggregate(
        total=Sum('credit')
    )['total'] or Decimal('0.00')

    # ======================
    # العملاء
    # ======================
    customers_count = Customer.objects.count()

    total_customer_balance = CustomerTransaction.objects.aggregate(
        total=Sum('balance')
    )['total'] or Decimal('0.00')

    # ======================
    # الحجوزات
    # ======================
    total_reservations = StearinReservation.objects.count()

    total_remaining = StearinReservation.objects.aggregate(
        total=Sum('remaining')
    )['total'] or Decimal('0.00')

    # ======================
    # آخر العمليات
    # ======================
    latest_supplier_tx = SupplierTransaction.objects.select_related('supplier').order_by('-date')[:5]
    latest_customer_tx = CustomerTransaction.objects.select_related('customer').order_by('-date')[:5]

    context = {
        # counters
        'suppliers_count': suppliers_count,
        'customers_count': customers_count,
        'total_reservations': total_reservations,

        # balances
        'total_supplier_balance': total_supplier_balance,
        'total_customer_balance': total_customer_balance,
        'total_remaining': total_remaining,

        # financial
        'total_debit': total_debit,
        'total_credit': total_credit,

        # tables
        'latest_supplier_tx': latest_supplier_tx,
        'latest_customer_tx': latest_customer_tx,
    }

    return render(request, 'dashboard/dashboard.html', context)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from decimal import Decimal

from .models import *


@api_view(['GET'])
def dashboard_api(request):

    data = {
        "suppliers_count": Supplier.objects.count(),
        "customers_count": Customer.objects.count(),
        "reservations_count": StearinReservation.objects.count(),

        "total_debit": SupplierTransaction.objects.aggregate(
            total=Sum('debit')
        )['total'] or 0,

        "total_credit": SupplierTransaction.objects.aggregate(
            total=Sum('credit')
        )['total'] or 0,

        "supplier_balance": SupplierTransaction.objects.aggregate(
            total=Sum('balance')
        )['total'] or 0,

        "customer_balance": CustomerTransaction.objects.aggregate(
            total=Sum('balance')
        )['total'] or 0,
    }

    return Response(data)

