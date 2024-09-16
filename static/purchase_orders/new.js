document.addEventListener('DOMContentLoaded', function() {
    // 自動填入供應商資訊
    const supplierSelect = document.getElementById('id_supplier');

    supplierSelect.addEventListener('change', function() {
        const supplierId = supplierSelect.value;
        fetch('/purchase_orders/load-supplier-info/?supplier_id=' + supplierId)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_supplier_tel').value = data.supplier_tel;
                document.getElementById('id_contact_person').value = data.contact_person;
                document.getElementById('id_supplier_email').value = data.supplier_email;
                // updateProductSelects(data.products);
                // console.log(data.products);
            })
    });

    function initializeProductSelects() {
        const selectedSupplierId = supplierSelect.value;
        if (selectedSupplierId) {
            fetch(window.djangoVariables.loadSupplierInfoUrl + '?supplier_id=' + selectedSupplierId)
                .then(response => response.json())
                .then(data => {
                    updateProductSelects(data.products);
                })
                .catch(error => console.error('Error fetching supplier info:', error));
        }
    }

    function updateProductSelects(products) {
        const productSelects = document.querySelectorAll('[id^="id_items-"][id$="-product"]');
        const productPrices = {}; // 儲存商品 ID 和價格的映射

        // 建立商品 ID 到價格的映射
        products.forEach(product => {
            productPrices[product.id] = product.price;
        });

        productSelects.forEach(select => {
            // 清空選項並重新設置
            select.innerHTML = '<option value="">---------</option>';

            products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = product.product_name;
                select.appendChild(option);
            });

            // 綁定商品選擇事件監聽器
            select.removeEventListener('change', handleProductChange);  // 先移除之前可能綁定的事件，避免重複
            select.addEventListener('change', handleProductChange);     // 然後綁定新的事件監聽器
        });

        function handleProductChange(event) {
            const selectedProductId = event.target.value;
            const priceFieldId = event.target.id.replace('-product', '-price');
            const priceField = document.getElementById(priceFieldId);

            if (selectedProductId) {
                const price = productPrices[selectedProductId] || '';
                priceField.value = price;
            } else {
                priceField.value = '';
            }
        }
    }

    // 子表單
    const addItemButton = document.getElementById('add-item')
    const formsetItems = document.getElementById('formset-items');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value);

    addItemButton.addEventListener('click',() => {
        const newItem = document.querySelector('#formset-items fieldset').cloneNode(true);
        newItem.innerHTML = newItem.innerHTML.replace(/items-(\d+)-/g, `items-${formCount}-`);
        newItem.querySelectorAll('input,select').forEach(element => {
            if (element.tagName === 'SELECT') {
                element.selectedIndex = 0;
            } else {
                element.value = '';
            }
        });
        formsetItems.appendChild(newItem);
        formCount++;
        totalForms.value = formCount;
    })

    formsetItems.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-item') && totalForms.value != 1) {
            const fieldset = event.target.closest('fieldset');
            fieldset.remove();
            updateFormIndexes();
            updateTotalAmount();
        }
    });
    function updateFormIndexes() {
        const formsets = formsetItems.querySelectorAll('fieldset');
        formsets.forEach((formset, index) => {
            formset.querySelectorAll('input, select').forEach((element) => {
                const name = element.getAttribute('name');
                const id = element.getAttribute('id');
                if (name) {
                    const newName = name.replace(/items-\d+-/, `items-${index}-`);
                    element.setAttribute('name', newName);
                }
                if (id) {
                    const newId = id.replace(/id_items-\d+-/, `id_items-${index}-`);
                    element.setAttribute('id', newId);
                }
            });
        });
        totalForms.value = formsets.length;
    }
    // 計算總價
    function updateTotalAmount() {
        const subtotalFields = document.querySelectorAll('[id$=subtotal]');
        let totalAmount = 0;
        subtotalFields.forEach(function(field) {
            const subtotal = parseInt(field.value, 10) || 0;
            totalAmount += subtotal;
        });
        document.getElementById('total-amount-display').textContent = totalAmount;
        document.getElementById('total_amount').value = totalAmount;
    }
    document.getElementById('formset-items').addEventListener('input', updateTotalAmount);
    updateTotalAmount();
});

