document.addEventListener('DOMContentLoaded', () => {
    const clientSelect = document.getElementById('id_client');
    const formsetItems = document.getElementById('formset-items');
    const addItemButton = document.getElementById('add-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    const salePriceInput = document.querySelector('input[name$="-sale_price"]');
    const stockQuantitySelects = document.querySelectorAll('select[name$="-stock_quantity"]');
    const orderedQuantityInput = document.querySelector('input[name$="-ordered_quantity"]');
    const shippedQuantityInput = document.querySelector('input[name$="-shipped_quantity"]');
    const orderedQuantityInputs = document.querySelectorAll('input[name$="-ordered_quantity"]');
    const shippedQuantityInputs = document.querySelectorAll('input[name$="-shipped_quantity"]');
    const subtotalInputs = document.querySelectorAll('input[name$="-subtotal"]');
    let formCount = parseInt(totalForms.value);

    shippedQuantityInputs.forEach(input => {
        input.setAttribute('min', '1');
    });
    orderedQuantityInputs.forEach(input => {
        input.setAttribute('min', '1');
    });
    subtotalInputs.forEach(input =>{
        input.readOnly = true;
    })
    // stockQuantitySelects.forEach(select =>{
    //     select.disabled = true;
    // })


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
        if (event.target.matches('input[name$="-shipped_quantity"], input[name$="-sale_price"]')) {
            const row = event.target.closest('fieldset');
            const shippedQuantityInput = row.querySelector('input[name$="-shipped_quantity"]');
            const salePriceInput = row.querySelector('input[name$="-sale_price"]');
            const subtotalInput = row.querySelector('input[name$="-subtotal"]');
            if (shippedQuantityInput && salePriceInput && subtotalInput) {
                subtotalInput.value = Math.round(shippedQuantityInput.value * salePriceInput.value);
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
        shippedQuantityInput.readOnly = disabled;
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
                const stockQuantitySelect = fieldset.querySelector('select[name$="-stock_quantity"]');
                const shippedQuantityInput = fieldset.querySelector('input[name$="-shipped_quantity"]');
                const orderedQuantityInput = fieldset.querySelector('input[name$="-ordered_quantity"]');
                const subtotalInput = fieldset.querySelector('input[name$="-subtotal"]');
                fetch(`/orders/load_product_info/?id=${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        salePriceInput.value = data.sale_price;
                        stockQuantitySelect.value = productId;
                        shippedQuantityInput.value = 1;
                        orderedQuantityInput.value = 1;
                        subtotalInput.value = shippedQuantityInput.value*salePriceInput.value;
                        updateTotalAmount();
                    });

            });
        });
    }
    updateTotalAmount();
});
