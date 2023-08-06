
function getDefaultItem(key, quantity, commit, discount) {
    return {
        key: key,
        description: res[key].description,
        setupfee: res[key].setupfee || 0,
        pricePerUnit: pricekey in res[key] ? res[key][pricekey] : res[key].price,
        quantity: quantity || 1,
        commit: commit || 1,
        discout: discount || 0,
    };
}