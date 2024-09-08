document.addEventListener('DOMContentLoaded', function() {
    const generateOrderNumberUrl = window.djangoVariables.generateOrderNumberUrl;

    fetch(generateOrderNumberUrl)
        .then(response => response.json())
        .then(data => {
            const orderNumberElement = document.getElementById('order-number');
            if (orderNumberElement) {
                orderNumberElement.textContent = data.order_number;
            }
        })
        .catch(error => console.error('Error fetching order number:', error));
});

document.addEventListener('DOMContentLoaded', function() {
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
});
