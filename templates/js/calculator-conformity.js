function renderConformitySelect() {
    const select = document.getElementById('conformity');

    select.innerHTML = CONFORMITY.map((c,i) => `<option value="${c}" ${c === conformity ? 'selected' : ''} >${c}</option>>`).join('');
    select.addEventListener('change', (e) => {
        conformity = select.value;
        pricekey = 'price_' + conformity;

        if (state.zones && state.zones.length && state.zones[0] && state.zones[0].items.length) {
            location.href = SerilizeState();
        }
    });
}