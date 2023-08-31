
function getItem(key, quantity, commit, discount) {
    let item = {
        key: key,
        description: index[key].description,
        setupfee: index[key].setupfee || 0,
        pricePerUnit: pricekey in index[key] ? index[key][pricekey] : index[key].price,
        quantity: quantity || 1,
        commit: commit || 1,
        discount: discount || 0,
    };
    item['setupfee'] *= item.quantity;
    item['total'] = item['pricePerUnit'] * item.quantity * (1 - (item.discount) / 100);
    return item;
}

function renderLegalCheckboxes() {
    const conditions = [
        ''
    ]
    const table = document.getElementById('legalcheckboxes');

}