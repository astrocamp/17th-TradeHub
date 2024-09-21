document.addEventListener('DOMContentLoaded', () => {
    const clientSelect = document.getElementById('id_client');
    const formsetItems = document.getElementById('formset-items');
    const addItemButton = document.getElementById('add-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    const salePriceInput = document.querySelector('input[name$="-sale_price"]');
    const orderedQuantityInput = document.querySelector('input[name$="-ordered_quantity"]');
    const orderedQuantityInputs = document.querySelectorAll('input[name$="-ordered_quantity"]');
    const subtotalInputs = document.querySelectorAll('input[name$="-subtotal"]');
    let formCount = parseInt(totalForms.value);

    orderedQuantityInputs.forEach(input => {
        input.setAttribute('min', '1');
    });
    subtotalInputs.forEach(input =>{
        input.readOnly = true;
    })


    // 自動填入客戶資訊
    if (clientSelect.value) {
        fetchClientInfo(clientSelect.value);
        toggleFormItems(false);
    } else {
        toggleFormItems(true);
    }

    clientSelect.addEventListener('change', () => {
        if (clientSelect.value) {
            fetchClientInfo(clientSelect.value);
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
        if (event.target.matches('input[name$="-ordered_quantity"], input[name$="-sale_price"]')) {
            const row = event.target.closest('fieldset');
            const orderedQuantityInput = row.querySelector('input[name$="-ordered_quantity"]');
            const salePriceInput = row.querySelector('input[name$="-sale_price"]');
            const subtotalInput = row.querySelector('input[name$="-subtotal"]');
            if (orderedQuantityInput && salePriceInput && subtotalInput) {
                subtotalInput.value = Math.round(orderedQuantityInput.value * salePriceInput.value);
                updateTotalAmount();
            }
        }
    });

    // 禁用或啟用子表單的商品選擇
    function toggleFormItems(disabled) {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            productSelect.disabled = disabled;
        });
        salePriceInput.readOnly = disabled;
        orderedQuantityInput.readOnly = disabled;
        addItemButton.disabled = disabled;
    }

    function fetchClientInfo(clientId) {
        fetch(`/orders/load_client_info/?client_id=${clientId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_client_tel').value = data.client_tel;
                document.getElementById('id_client_address').value = data.client_address;
                document.getElementById('id_client_email').value = data.client_email;
                handleProductChange();
                const salePriceInputs = document.querySelectorAll('input[name$="-sale_price"]');
                // salePriceInputs.forEach(input => {
                //     input.value = '';
                // });
                // orderedQuantityInputs.forEach(input => {
                //     input.value = '';
                // });
                // subtotalInputs.forEach(input => {
                //     input.value = '';
                // });
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
                const salePriceInput = fieldset.querySelector('input[name$="-sale_price"]');
                const orderdQuantityInput = fieldset.querySelector('input[name$="-ordered_quantity"]');
                const subtotalInput = fieldset.querySelector('input[name$="-subtotal"]');
                fetch(`/orders/load_product_info/?id=${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        salePriceInput.value = data.sale_price;
                        orderdQuantityInput.value = 1;
                        subtotalInput.value = orderdQuantityInput.value*salePriceInput.value;
                        updateTotalAmount();
                    });

            });
        });
    }
    updateTotalAmount();
});
