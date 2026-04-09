from django.contrib import admin
from django import forms
from .models import Supplier, SupplierTransaction,Customer,CustomerTransaction,StearinReservation




@admin.register(StearinReservation)
class StearinReservationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'date',
        'quantity',
        'price',
        'addition',
        'deduction',
        'driver_name',
        'total_addition',
        'remaining',
    )

    readonly_fields = (
        'total_addition',
        'remaining',
    )

    search_fields = (
        'driver_name',
    )

    list_filter = (
        'date',
    )

    ordering = ('-date', '-id')

@admin.register(CustomerTransaction)
class CustomerTransactionAdmin(admin.ModelAdmin):

    list_display = (
        'customer',
        'date',
        'quantity',
        'sale_price',
        'total_sale',
        'payment',
        'balance',
        'status',
    )

    list_filter = (
        'date',
        'customer',
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'address',
        'phone',
        'current_balance',
        'status',
    )

    search_fields = ('name', 'phone')

    # 🔹 الرصيد الحالي
    def current_balance(self, obj):
        from .models import SupplierTransaction

        # مؤقتًا هنحسب من نفس جدول العمليات
        # (بعد كده ممكن نعمل CustomerTransaction منفصل)
        last = SupplierTransaction.objects.filter(
            supplier__name=obj.name
        ).order_by('-date', '-id').first()

        return last.balance if last else obj.opening_balance

    current_balance.short_description = "الرصيد الحالي"

    # 🔹 الحالة
    def status(self, obj):
        balance = self.current_balance(obj)

        if balance > 0:
            return "علينا"
        elif balance < 0:
            return "لينا"
        return "متوازن"

    status.short_description = "الحالة"
# ===============================
# Custom Form (Validation)
# ===============================
class SupplierTransactionForm(forms.ModelForm):
    class Meta:
        model = SupplierTransaction
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get('transaction_type')
        purchase_price = cleaned_data.get('purchase_price')
        sale_price = cleaned_data.get('sale_price')

        if transaction_type == 'purchase' and purchase_price is None:
            raise forms.ValidationError("لازم تدخل سعر شراء")

        if transaction_type == 'sale' and sale_price is None:
            raise forms.ValidationError("لازم تدخل سعر بيع")

        return cleaned_data


# ===============================
# Supplier Admin (Tab الموردين)
# ===============================
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'address',
        'phone',
        'current_balance',
        'status',
    )

    search_fields = ('name', 'phone')

    # 🔹 حساب الرصيد الحالي
    def current_balance(self, obj):
        last = SupplierTransaction.objects.filter(
            supplier=obj
        ).order_by('-date', '-id').first()

        return last.balance if last else obj.opening_balance

    current_balance.short_description = "الرصيد الحالي"

    # 🔹 الحالة
    def status(self, obj):
        balance = self.current_balance(obj)

        if balance > 0:
            return "علينا"
        elif balance < 0:
            return "لينا"
        return "متوازن"

    status.short_description = "الحالة"


# ===============================
# Transaction Admin (نموذج مورد)
# ===============================
@admin.register(SupplierTransaction)
class SupplierTransactionAdmin(admin.ModelAdmin):

    form = SupplierTransactionForm

    class Media:
        js = ('admin/js/supplier.js',)

    list_display = (
        'supplier_name',
        'date',
        'transaction_type_ar',
        'quantity',
        'oil_type_ar',
        'total_purchase',
        'total_sale',
        'payment',
        'balance',
        'status',
    )

    list_filter = (
        'transaction_type',
        'date',
        'supplier',
        'oil_type',
    )

    search_fields = (
        'supplier__name',
        'driver_name',
        'car_name',
        'description',
    )

    ordering = ('-date', '-id')

    readonly_fields = (
        'total_purchase',
        'total_sale',
        'debit',
        'credit',
        'balance',
        'status',
    )

    fieldsets = (

        ("البيانات الأساسية", {
            'fields': (
                'supplier',   # 👈 رجعناه
                'transaction_type',
                'date',
                'quantity',
            )
        }),

        ("الأسعار", {
            'fields': (
                'purchase_price',
                'sale_price',
            )
        }),

        ("تفاصيل إضافية", {
            'fields': (
                'oil_type',
                'driver_name',
                'car_name',
                'description',
            )
        }),

        ("الحسابات", {
            'fields': (
                'payment',
                'total_purchase',
                'total_sale',
                'debit',
                'credit',
                'balance',
                'status',
            )
        }),
    )

    # ======================
    # 🔹 Display Methods
    # ======================

    def supplier_name(self, obj):
        return obj.supplier.name
    supplier_name.short_description = "المورد"

    def transaction_type_ar(self, obj):
        return obj.get_transaction_type_display()
    transaction_type_ar.short_description = "نوع العملية"

    def oil_type_ar(self, obj):
        return obj.get_oil_type_display() if obj.oil_type else "-"
    oil_type_ar.short_description = "نوع الزيت"