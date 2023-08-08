
function getItem(key, quantity, commit, discount) {
    console.log(res[key]);
    let item = {
        key: key,
        description: res[key].description,
        setupfee: res[key].setupfee || 0,
        pricePerUnit: pricekey in res[key] ? res[key][pricekey] : res[key].price,
        quantity: quantity || 1,
        commit: commit || 1,
        discount: discount || 0,
    };
    item['setupfee'] *= item.quantity;
    item['total'] = item['pricePerUnit'] * item.quantity * (1 - (item.discount) / 100);
    return item;
}