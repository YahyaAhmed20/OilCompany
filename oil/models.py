# suppliers/models.py

from django.db import models
from decimal import Decimal


class Supplier(models.Model):
    name = models.CharField("اسم المورد", max_length=255)

    address = models.CharField("العنوان", max_length=255, blank=True, null=True)
    phone = models.CharField("التليفون", max_length=20, blank=True, null=True)

    opening_balance = models.DecimalField(
        "رصيد أول المدة",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"

    def __str__(self):
        return self.name


class SupplierTransaction(models.Model):

    TRANSACTION_TYPE = [
        ('purchase', 'شراء'),
        ('sale', 'بيع'),
    ]
    
    OIL_TYPE_CHOICES = [
    ('olein_rbd', 'أولين RBD'),
    ('olein_refined', 'أولين مكرر'),
    ('stearin', 'استيارين'),
    ('palm_rbd', 'النخيل RBD'),
    ('palm_refined', 'النخيل مكرر'),
    ('kernel_olein', 'نواه أولين'),
    ('palm_kernel', 'نواه نخيل'),
    ('sunflower_refined', 'عباد مكرر'),
    ('soybean_refined', 'صويا مكرر'),
]

    supplier = models.ForeignKey(
        Supplier,
        verbose_name="المورد",
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        "نوع العملية",
        max_length=10,
        choices=TRANSACTION_TYPE
    )

    date = models.DateField("التاريخ")

    quantity = models.DecimalField(
        "الحمولة",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    purchase_price = models.DecimalField(
        "سعر شراء الزيت",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    sale_price = models.DecimalField(
        "سعر بيع الزيت",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    oil_type = models.CharField(
    "نوع الزيت",
    max_length=50,
    choices=OIL_TYPE_CHOICES,
    null=True,
    blank=True
)

    driver_name = models.CharField(
        "اسم السائق",
        max_length=255,
        null=True,
        blank=True
    )

    car_name = models.CharField(
        "اسم السيارة",
        max_length=255,
        null=True,
        blank=True
    )

    description = models.TextField(
        "بيان",
        null=True,
        blank=True
    )

    payment = models.DecimalField(
        "تنزيل من الحساب",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    total_purchase = models.DecimalField(
        "إجمالي الشراء",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    total_sale = models.DecimalField(
        "إجمالي البيع",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    debit = models.DecimalField(
        "علينا",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    credit = models.DecimalField(
        "لينا",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    balance = models.DecimalField(
        "الرصيد الصافي",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        "الحالة",
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نموذج مورد"
        verbose_name_plural = "نماذج الموردين"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):

        zero = Decimal('0.00')

        quantity = self.quantity or zero
        purchase_price = self.purchase_price or zero
        sale_price = self.sale_price or zero
        payment = self.payment or zero

        # 1) حساب الإجماليات
        self.total_purchase = quantity * purchase_price
        self.total_sale = quantity * sale_price

        # 2) علينا / لينا
        if self.transaction_type == 'purchase':
            self.debit = self.total_purchase
            self.credit = zero

        elif self.transaction_type == 'sale':
            self.debit = zero
            self.credit = self.total_sale

        # 3) التنزيل
        self.credit += payment

        # 4) آخر رصيد (مع استثناء الحالي)
        last_transaction = SupplierTransaction.objects.filter(
            supplier=self.supplier
        ).exclude(id=self.id).order_by('-date', '-id').first()

        if last_transaction:
            last_balance = last_transaction.balance
        else:
            last_balance = self.supplier.opening_balance

        # 5) حساب الرصيد
        self.balance = last_balance + self.debit - self.credit

        # 6) الحالة
        if self.balance > 0:
            self.status = "علينا"
        elif self.balance < 0:
            self.status = "لينا"
        else:
            self.status = "متوازن"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier.name} - {self.get_transaction_type_display()} - {self.date}"
    
    
    
    
class Customer(models.Model):
    name = models.CharField("اسم العميل", max_length=255)

    address = models.CharField("العنوان", max_length=255, blank=True, null=True)
    phone = models.CharField("التليفون", max_length=20, blank=True, null=True)

    opening_balance = models.DecimalField(
        "رصيد أول المدة",
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

    def __str__(self):
        return self.name
    
    
    
    from decimal import Decimal

class CustomerTransaction(models.Model):

    TRANSACTION_TYPE = [
        ('sale', 'بيع'),
    ]

    customer = models.ForeignKey(
        Customer,
        verbose_name="العميل",
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        "نوع العملية",
        max_length=10,
        choices=TRANSACTION_TYPE,
        default='sale'
    )

    date = models.DateField("التاريخ")

    quantity = models.DecimalField(
        "الكمية",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    sale_price = models.DecimalField(
        "سعر البيع",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    description = models.TextField("بيان", blank=True, null=True)

    payment = models.DecimalField(
        "تحصيل من العميل",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # =====================
    # القيم المحسوبة
    # =====================
    total_sale = models.DecimalField(
        "إجمالي البيع",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    debit = models.DecimalField(
        "علينا (العميل مدين)",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    credit = models.DecimalField(
        "سدد (دفع)",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    balance = models.DecimalField(
        "الرصيد",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField("الحالة", max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "حركة عميل"
        verbose_name_plural = "حركات العملاء"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):

        zero = Decimal('0.00')

        quantity = self.quantity or zero
        sale_price = self.sale_price or zero
        payment = self.payment or zero

        # 1) إجمالي البيع
        self.total_sale = quantity * sale_price

        # 2) العميل مدين
        self.debit = self.total_sale

        # 3) اللي دفعه
        self.credit = payment

        # 4) آخر رصيد
        last_transaction = CustomerTransaction.objects.filter(
            customer=self.customer
        ).exclude(id=self.id).order_by('-date', '-id').first()

        if last_transaction:
            last_balance = last_transaction.balance
        else:
            last_balance = self.customer.opening_balance

        # 5) الرصيد الجديد
        self.balance = last_balance + self.debit - self.credit

        # 6) الحالة
        if self.balance > 0:
            self.status = "علينا"
        elif self.balance < 0:
            self.status = "لنا"
        else:
            self.status = "متوازن"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.date}"
    
    
    
from decimal import Decimal

class StearinReservation(models.Model):

    date = models.DateField("التاريخ")

    quantity = models.DecimalField(
        "الكمية",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    price = models.DecimalField(
        "السعر",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    addition = models.DecimalField(
        "إضافة",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    deduction = models.DecimalField(
        "تنزيل",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    driver_name = models.CharField(
        "اسم السائق",
        max_length=255,
        blank=True,
        null=True
    )

    total_addition = models.DecimalField(
        "إجمالي الإضافة",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    remaining = models.DecimalField(
        "الباقي من التنزيل",
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "حجز زيت استيارين"
        verbose_name_plural = "حجوزات زيت استيارين"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):

        zero = Decimal('0.00')

        quantity = self.quantity or zero
        price = self.price or zero
        addition = self.addition or zero
        deduction = self.deduction or zero

        # 1) إجمالي الإضافة
        self.total_addition = quantity * price + addition

        # 2) آخر رصيد
        last = StearinReservation.objects.exclude(id=self.id).order_by('-date', '-id').first()

        if last:
            last_remaining = last.remaining
        else:
            last_remaining = zero

        # 3) الباقي
        self.remaining = last_remaining + self.total_addition - deduction

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.driver_name or ''}"