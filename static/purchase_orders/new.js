document.addEventListener('DOMContentLoaded', function() {
    // 自動填入供應商資訊
    const supplierSelect = document.getElementById(window.djangoVariables.supplierIdField);

    supplierSelect.addEventListener('change', function() {
        const supplierId = supplierSelect.value;

        fetch(window.djangoVariables.loadSupplierInfoUrl + '?supplier_id=' + supplierId)
            .then(response => response.json())
            .then(data => {
                // Update supplier details
                document.getElementById(window.djangoVariables.supplierTelField).value = data.supplier_tel;
                document.getElementById(window.djangoVariables.contactPersonField).value = data.contact_person;
                document.getElementById(window.djangoVariables.supplierEmailField).value = data.supplier_email;
            })
            .catch(error => console.error('Error fetching supplier info:', error));
    });

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
            console.log(fieldset)
            updateFormIndexes();
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
});

