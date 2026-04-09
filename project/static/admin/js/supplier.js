document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // 🔹 إظهار / إخفاء الحقول
    // =========================
    function toggleFields() {
        const typeField = document.getElementById("id_transaction_type");

        const purchaseField = document.querySelector(".form-row.field-purchase_price");
        const saleField = document.querySelector(".form-row.field-sale_price");

        if (!typeField) return;

        if (typeField.value === "purchase") {
            if (purchaseField) purchaseField.style.display = "";
            if (saleField) saleField.style.display = "none";
        } else if (typeField.value === "sale") {
            if (purchaseField) purchaseField.style.display = "none";
            if (saleField) saleField.style.display = "";
        }
    }

    // =========================
    // 🔹 حساب Live
    // =========================
    function liveCalculation() {
        const quantity = parseFloat(document.getElementById("id_quantity")?.value || 0);
        const purchasePrice = parseFloat(document.getElementById("id_purchase_price")?.value || 0);
        const salePrice = parseFloat(document.getElementById("id_sale_price")?.value || 0);
        const payment = parseFloat(document.getElementById("id_payment")?.value || 0);

        const typeField = document.getElementById("id_transaction_type");

        if (!typeField) return;

        let totalPurchase = quantity * purchasePrice;
        let totalSale = quantity * salePrice;

        let debit = 0;
        let credit = 0;

        if (typeField.value === "purchase") {
            debit = totalPurchase;
            credit = 0;
        } else if (typeField.value === "sale") {
            debit = 0;
            credit = totalSale;
        }

        credit += payment;

        // 🔹 تحديث القيم في الفورم
        function setVal(id, val) {
            const el = document.getElementById(id);
            if (el) el.value = val.toFixed(2);
        }

        setVal("id_total_purchase", totalPurchase);
        setVal("id_total_sale", totalSale);
        setVal("id_debit", debit);
        setVal("id_credit", credit);
    }

    // =========================
    // 🔹 Events
    // =========================

    // تغيير نوع العملية
    document.addEventListener("change", function (e) {
        if (e.target.id === "id_transaction_type") {
            toggleFields();
            liveCalculation();
        }
    });

    // إدخال بيانات
    document.addEventListener("input", function (e) {
        if (
            e.target.id === "id_quantity" ||
            e.target.id === "id_purchase_price" ||
            e.target.id === "id_sale_price" ||
            e.target.id === "id_payment"
        ) {
            liveCalculation();
        }
    });

    // تشغيل عند فتح الصفحة
    toggleFields();
    liveCalculation();
});