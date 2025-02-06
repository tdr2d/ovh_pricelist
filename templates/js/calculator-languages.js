const LANGUAGES = [
    { 'code': 'fr', 'name': 'French (FR)'},
    { 'code': 'en', 'name': 'English (EN)'},
    { 'code': 'de', 'name': 'Deutsch (DE)'},
];

function renderLanguages(state) {
    const selected = state.lang;
    const options = LANGUAGES.map(l => `<option ${selected == l.code ? 'selected' : ''} value='${l.code}'>${l.name}</option>`)

    document.getElementById('languages-placeholder').innerHTML = `
    <select class="form-select form-select-sm">
        ${options.join('')}
    </select>`;

    document.querySelector('#languages-placeholder > select').addEventListener('change', onChangeLanguage);
}

function onChangeLanguage(e) {
    state.lang = e.target.value;
    renderLegalCheckboxes();
}