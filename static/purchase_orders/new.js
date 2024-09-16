document.addEventListener('DOMContentLoaded', function() {
    // 自動填入供應商資訊
    const supplierSelect = document.getElementById('id_supplier');

    // 檢查頁面載入時是否有選中的供應商
    if (supplierSelect.value) {
        fetchSupplierInfo(supplierSelect.value);
    }

    supplierSelect.addEventListener('change', function() {
        const supplierId = supplierSelect.value;
        fetchSupplierInfo(supplierId);
    });

    function fetchSupplierInfo(supplierId) {
        fetch('/purchase_orders/load-supplier-info/?supplier_id=' + supplierId)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_supplier_tel').value = data.supplier_tel;
                document.getElementById('id_contact_person').value = data.contact_person;
                document.getElementById('id_supplier_email').value = data.supplier_email;
                updateProductOptions(data.products);
            });
    }

    function updateProductOptions(products) {
        document.querySelectorAll('[id^="id_items-"][id$="-product"]').forEach(function(productSelect) {
            // 保存目前選擇的商品
            const selectedProduct = productSelect.value;

            productSelect.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '---------';
            productSelect.appendChild(defaultOption);

            // 生成新的商品選項
            products.forEach(function(product) {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = product.product_name;

                // 保留已選擇的商品選項
                if (product.id == selectedProduct) {
                    option.selected = true;
                }

                productSelect.appendChild(option);
            });
        });
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

