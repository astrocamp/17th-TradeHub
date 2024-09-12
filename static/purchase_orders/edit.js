document.addEventListener('DOMContentLoaded', function() {

    const addItemButton = document.getElementById('add-item')
    const deleteButtons = document.querySelectorAll('.delete-item');
    const formsetItems = document.getElementById('formset-items');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value);

    // 新增欄位
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

    // 刪除欄位
    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const fieldset = event.target.closest('fieldset');
            const deleteCheckbox = fieldset.querySelector('input[name$="-DELETE"]');

            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                fieldset.style.display = 'none';
            }
        });
    });
});