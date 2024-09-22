document.addEventListener('DOMContentLoaded', () => {
    const clientSelect = document.getElementById('id_client');
    const formsetItems = document.getElementById('formset-items');
    const addItemButton = document.getElementById('add-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    const stockQuantitySelects = document.querySelectorAll('select[name$="-stock_quantity"]');
    const orderedQuantityInputs = document.querySelectorAll('input[name$="-ordered_quantity"]');
    const clientInput = document.querySelector('select[name="client"]');
    const subtotalInputs = document.querySelectorAll('input[name$="-subtotal"]');
    let formCount = parseInt(totalForms.value);

    clientInput.addEventListener('mousedown', (e) => {
        e.preventDefault();
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
            const fieldset = event.target.closest('fieldset');
            const deleteField = fieldset.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (deleteField) {
                deleteField.checked = true;
            }
            fieldset.style.display = 'none';
            formCount--;
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
        const totalAmount = Array.from(document.querySelectorAll('#formset-items fieldset'))
            .filter(fieldset => fieldset.style.display !== 'none')
            .reduce((sum, fieldset) => {
                const subtotalInput = fieldset.querySelector('input[name$="-subtotal"]');
                return sum + (parseInt(subtotalInput.value, 10) || 0);
            }, 0);

        document.getElementById('total-amount-display').textContent = totalAmount;
        document.getElementById('amount').value = totalAmount;
    }

    function handleProductChange() {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(productSelect => {
            productSelect.addEventListener('change', function() {
                const productId = this.value;
                const fieldset = this.closest('fieldset');
                const stockQuantitySelect = fieldset.querySelector('select[name$="-stock_quantity"]');
                const salePriceInput = fieldset.querySelector('input[name$="-sale_price"]');
                const orderedQuantityInput = fieldset.querySelector('input[name$="-ordered_quantity"]');
                const subtotalInput = fieldset.querySelector('input[name$="-subtotal"]');
                fetch(`/orders/load_product_info/?id=${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        stockQuantitySelect.value = productId;
                        salePriceInput.value = data.sale_price;
                        orderedQuantityInput.value = 1;
                        subtotalInput.value = orderedQuantityInput.value*salePriceInput.value;
                        updateTotalAmount();
                    });

            });
        });
    }
    updateTotalAmount();
});
