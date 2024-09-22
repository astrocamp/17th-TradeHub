document.addEventListener('DOMContentLoaded', () => {
    const supplierSelect = document.getElementById('id_supplier');
    const formsetItems = document.getElementById('formset-items');
    const addItemButton = document.getElementById('add-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    const costPriceInput = document.querySelector('input[name$="-cost_price"]');
    const orderedQuantityInput = document.querySelector('input[name$="-ordered_quantity"]');
    const receivedQuantityInput = document.querySelector('input[name$="-received_quantity"]');
    const orderedQuantityInputs = document.querySelectorAll('input[name$="-ordered_quantity"]');
    const receivedQuantityInputs = document.querySelectorAll('input[name$="-received_quantity"]');
    const subtotalInputs = document.querySelectorAll('input[name$="-subtotal"]');
    let formCount = parseInt(totalForms.value);

    orderedQuantityInputs.forEach(input => {
        input.setAttribute('min', '1');
    });
    receivedQuantityInputs.forEach(input => {
        input.setAttribute('min', '1');
    });
    subtotalInputs.forEach(input =>{
        input.readOnly = true;
    })
    // 禁用或啟用子表單的商品選擇
    function toggleFormItems(disabled) {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            productSelect.disabled = disabled;
        });
        costPriceInput.readOnly = disabled;
        orderedQuantityInput.readOnly = disabled;
        receivedQuantityInput.readOnly = disabled;
        addItemButton.disabled = disabled;
    }

    // 自動填入供應商資訊
    if (supplierSelect.value) {
        fetchSupplierInfo(supplierSelect.value);
        toggleFormItems(false);
    } else {
        toggleFormItems(true);
    }

    supplierSelect.addEventListener('change', () => {
        if (supplierSelect.value) {
            fetchSupplierInfo(supplierSelect.value);
            toggleFormItems(false);
        } else {
            toggleFormItems(true);
        }
    });
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
            formCount--;
            event.target.closest('fieldset').remove();
            updateFormIndexes();
            updateTotalAmount();
        }
    });

    // 計算金額
    formsetItems.addEventListener('input', (event) => {
        if (event.target.matches('input[name$="-received_quantity"], input[name$="-cost_price"]')) {
            const row = event.target.closest('fieldset');
            const receivedQuantity = row.querySelector('input[name$="-received_quantity"]');
            const costPriceInput = row.querySelector('input[name$="-cost_price"]');
            const subtotalInput = row.querySelector('input[name$="-subtotal"]');
            if (receivedQuantity && costPriceInput && subtotalInput) {
                subtotalInput.value = Math.round(receivedQuantity.value * costPriceInput.value);
                updateTotalAmount();
            }
        }
    });

    function fetchSupplierInfo(supplierId) {
        fetch(`/goods_receipts/load_supplier_info/?supplier_id=${supplierId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_supplier_tel').value = data.supplier_tel;
                document.getElementById('id_contact_person').value = data.contact_person;
                document.getElementById('id_supplier_email').value = data.supplier_email;
                updateProductOptions(data.products);
                const receivedQuantityInput = document.querySelectorAll('input[name$="-received_quantity"]');
                const costPriceInputs = document.querySelectorAll('input[name$="-cost_price"]');
                const orderedQuantityInputs = document.querySelectorAll('input[name$="-ordered_quantity"]');
                const subtotalInputs = document.querySelectorAll('input[name$="-subtotal"]');
                receivedQuantityInput.forEach(input => {
                    input.value = '';
                });
                costPriceInputs.forEach(input => {
                    input.value = '';
                });
                orderedQuantityInputs.forEach(input => {
                    input.value = '';
                });
                subtotalInputs.forEach(input => {
                    input.value = '';
                });
                updateTotalAmount();
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
        document.getElementById('amount').value = totalAmount;
    }

    function handleProductChange() {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            productSelect.addEventListener('change', function() {
                const productId = this.value;
                const fieldset = this.closest('fieldset');
                const costPriceInput = fieldset.querySelector('input[name$="-cost_price"]');
                const receivedQuantityInput = fieldset.querySelector('input[name$="-received_quantity"]');
                const orderedQuantityInput = fieldset.querySelector('input[name$="-ordered_quantity"]');
                const subtotalInput = fieldset.querySelector('input[name$="-subtotal"]');
                fetch(`/purchase_orders/load_product_info/?id=${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        costPriceInput.value = data.cost_price;
                        orderedQuantityInput.value = 1;
                        receivedQuantityInput.value = 1;
                        subtotalInput.value = receivedQuantityInput.value*costPriceInput.value;
                        updateTotalAmount();
                    });

            });
        });
    }
    updateTotalAmount();
});
