document.addEventListener('DOMContentLoaded', () => {
    const supplierSelect = document.getElementById('id_supplier');
    const formsetItems = document.getElementById('formset-items');
    const addItemButton = document.getElementById('add-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value, 10);

    // 自動填入供應商資訊
    if (supplierSelect.value) fetchSupplierInfo(supplierSelect.value);
    supplierSelect.addEventListener('change', () => fetchSupplierInfo(supplierSelect.value));
    handleProductChange();

    // 新增子表單項目
    addItemButton.addEventListener('click', () => {
        const newItem = document.querySelector('#formset-items fieldset').cloneNode(true);
        newItem.innerHTML = newItem.innerHTML.replace(/items-(\d+)-/g, `items-${formCount}-`);
        newItem.querySelectorAll('input, select').forEach(element => {
            element.value = '';
            if (element.tagName === 'SELECT') element.selectedIndex = 0;
        });
        formsetItems.appendChild(newItem);
        formCount++;
        totalForms.value = formCount;
        handleProductChange();
    });

    // 刪除子表單項目
    formsetItems.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-item') && formCount > 1) {
            event.target.closest('fieldset').remove();
            updateFormIndexes();
            updateTotalAmount();
        }
    });

    // 計算金額
    formsetItems.addEventListener('input', (event) => {
        if (event.target.matches('input[name$="-quantity"], input[name$="-cost_price"]')) {
            const row = event.target.closest('fieldset');
            const quantityInput = row.querySelector('input[name$="-quantity"]');
            const costPriceInput = row.querySelector('input[name$="-cost_price"]');
            const subtotalInput = row.querySelector('input[name$="-subtotal"]');
            if (quantityInput && costPriceInput && subtotalInput) {
                const quantity = parseFloat(quantityInput.value) || 0;
                const costPrice = parseFloat(costPriceInput.value) || 0;
                subtotalInput.value = Math.round(quantity * costPrice);
                updateTotalAmount();
            }
        }
    });

    formsetItems.addEventListener('change',() => {

    })

    function fetchSupplierInfo(supplierId) {
        fetch(`/purchase_orders/load_supplier_info/?supplier_id=${supplierId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_supplier_tel').value = data.supplier_tel;
                document.getElementById('id_contact_person').value = data.contact_person;
                document.getElementById('id_supplier_email').value = data.supplier_email;
                updateProductOptions(data.products);
            });
    }

    function updateProductOptions(products) {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            const selectedProduct = productSelect.value;
            productSelect.innerHTML = '<option value="">---------</option>';
            products.forEach(product => {
                const option = new Option(product.product_name, product.id, false, product.id == selectedProduct);
                productSelect.appendChild(option);
            });
        });
    }

    function updateFormIndexes() {
        formsetItems.querySelectorAll('fieldset').forEach((fieldset, index) => {
            fieldset.querySelectorAll('input, select').forEach(element => {
                const name = element.getAttribute('name');
                const id = element.getAttribute('id');
                if (name) element.setAttribute('name', name.replace(/items-\d+-/, `items-${index}-`));
                if (id) element.setAttribute('id', id.replace(/id_items-\d+-/, `id_items-${index}-`));
            });
        });
        totalForms.value = formsetItems.querySelectorAll('fieldset').length;
    }

    function updateTotalAmount() {
        const totalAmount = Array.from(document.querySelectorAll('[id$="-subtotal"]'))
            .reduce((sum, field) => sum + (parseInt(field.value, 10) || 0), 0);
        document.getElementById('total-amount-display').textContent = totalAmount;
        document.getElementById('total_amount').value = totalAmount;
    }

    function fetchCostPrice(productId, callback) {
        fetch(`/purchase_orders/load-product-info/?product_id=${productId}`)
            .then(response => response.json())
            .then(data => {
                callback(data.cost_price); // 將抓取的 cost_price 傳遞給回調函數
            });
    }

    function handleProductChange() {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            productSelect.addEventListener('change', function() {
                const productId = this.value;
                const fieldset = this.closest('fieldset');
                const costPriceInput = fieldset.querySelector('input[name$="-cost_price"]');
                fetch(`/purchase_orders/load_product_info/?product_id=${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        costPriceInput.value = data.cost_price;
                    });

            });
        });
    }
    updateTotalAmount();
});
