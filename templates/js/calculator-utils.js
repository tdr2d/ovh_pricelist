const COORDINATES_TO_SAVE_FORMULA = [
    'J20','J21','J22','J23','J24','J25','J26','J27', 'J28',
];
const SPECIAL_CELLS = {
    'client': 'B10',
    'client_2': 'D10',
    'author': 'G7',
    'zone_width': 'A-J',
    'item_width': 'A-D',
    'row_ref_zone': 16,
    'row_ref_item': 17,
    'currency': 'C6',
    'taxe_name': 'C7', 'taxe_rate': 'C8',
    'support_name': 'C9', 'support_percent': 'C10', 'support_min': 'C11',
    'exceptionnal_discount': 'C12',
    'budget_duration': 'C13',
    'legal_start': 'A61'
};
const SUPPORT_KEY_TO_NAME = {'e': 'entreprise', 'b': 'business', 's': 'standard'};
const PREFIX_LEGAL_TEXT = 'Conditions Particulières ';
const PREFIX_ZONE_TEXT = 'Zone ';
const price_formula = (row) => `F${row}*G${row}*(1-I${row})`;
const cell_vertical_offset = (coord, offset) => coord.replace(/([A-Z]+)([0-9]+)/g, (m,col,row)=>`${col}${parseInt(row)+offset}`);

function getItemRowHeightFromDescription(description) {
    return description.split('\n').length * 10 * 1.4;
}

function DC_key_to_text(key) {
    return `${key} - ${DCS[key].city} (${DCS[key].country})`;
}

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

function saveXLSX(state, currency) {
    getXLSXTemplate(XLSX_TEMPLATE, XLSX_SHEETNAME).then(sheet => {
        sheet.getCell(SPECIAL_CELLS['client']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['client_2']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['author']).value = state.author;
        sheet.getCell(SPECIAL_CELLS['currency']).value = currency;
        sheet.getCell(SPECIAL_CELLS['support_name']).value = SUPPORT_KEY_TO_NAME[state.support];
        sheet.getCell(SPECIAL_CELLS['support_percent']).value = SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].percent;
        sheet.getCell(SPECIAL_CELLS['support_min']).value = SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].minimum;
        sheet.getCell(SPECIAL_CELLS['exceptionnal_discount']).value = state.totaldiscount;

        // Display legals
        let legal_count = 0;
        for (const key of state.legal_checked.split('')) {
            const text_cell = cell_vertical_offset(SPECIAL_CELLS['legal_start'], legal_count);
            const url_cell = cell_vertical_offset(SPECIAL_CELLS['legal_start'], legal_count+1);
            sheet.getCell(text_cell).value =  PREFIX_LEGAL_TEXT + res.legal[LANG][key].text;
            sheet.getCell(text_cell).style =  {'font': {'bold': true, 'size': 10}};
            sheet.getCell(url_cell).value =  {'text': res.legal[LANG][key].url, 'hyperlink': res.legal[LANG][key].url};
            legal_count += 2;
        }

        // Display zones and items
        let offset = -2;
        let row_index = SPECIAL_CELLS.row_ref_item + 1;
        for (const zone of state.zones) {
            if (offset < 0) {
                sheet.getCell(`A${row_index - 2}`).value = PREFIX_ZONE_TEXT + DC_key_to_text(zone['key']);
            } else {
                row_index = insertZoneRow(sheet, row_index, PREFIX_ZONE_TEXT + DC_key_to_text(zone['key']))
            }
            offset += 1;
            for (const item of zone['items']) {
                if (offset < 0) {
                    const row = sheet.getRow(row_index - 1);
                    const item_keys = ['description', 'description', 'description', 'description', 'setupfee', 'pricePerUnit', 'quantity', 'commit', 'discount']
                    for (const i in item_keys) {
                        row.getCell(parseInt(i)+1).value = (item_keys[i] == 'discount') ? item[item_keys[i]]/100 : item[item_keys[i]];
                    }
                    row.height = getItemRowHeightFromDescription(item['description']);
                } else {
                    row_index = insertPriceRow(sheet, row_index, item.description, item.setupfee, item.pricePerUnit, item.quantity, item.commit, item.discount/100);
                }
                offset += 1;
            }
        }
        update_formula(sheet, COORDINATES_TO_SAVE_FORMULA, offset);
        return sheet._workbook.xlsx.writeBuffer();
    })
    .then(buffer => saveByteArray([buffer], 'test.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
}

var saveByteArray = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (data, name, type) {
        var blob = new Blob(data, {type: type || "octet/stream"}),
            url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = name;
        a.click();
        window.URL.revokeObjectURL(url);
    };
}());

// Add a vertical offset to all saved_formulas
function update_formula(sheet, old_coordinates, voffset) {
    console.log(voffset);
    for (const i in old_coordinates) {
        const new_coord = cell_vertical_offset(old_coordinates[i], voffset);
        const old_formula = sheet.getCell(new_coord).formula;
        // regex https://regex101.com/r/SHrdes/1
        const new_formula = old_formula.replace(/(^|[^(])([A-Z]+)([1-9][0-9]*)/g, (m, p0,p1,p2) => `${p0}${p1}${parseInt(p2)+voffset}`);
        console.log({old: old_coordinates[i], new: new_coord, old_formula: old_formula, new_formula: new_formula})
        sheet.getCell(new_coord).value = {formula: new_formula};
    }
}

function insertPriceRow(sheet, rowIndex, description, installCost, unitCost, quantity, commitDuration, commitDiscount) {
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_item);
    const row_values = [description, description, description, description, installCost, unitCost, quantity, commitDuration, commitDiscount, {formula: price_formula(rowIndex)}];
    const new_row = sheet.insertRow(rowIndex, row_values, 'i');
    const s_e = SPECIAL_CELLS['item_width'].split('-');
    sheet.mergeCells(`${s_e[0]}${rowIndex}:${s_e[1]}${rowIndex}`);
    for (const i in row_ref._cells) {
        new_row._cells[i].style = row_ref._cells[i].style;
    }
    new_row.height = getItemRowHeightFromDescription(description);
    return rowIndex + 1;
}

function insertZoneRow(sheet, rowIndex, zoneDescription) {
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_zone);
    const new_row = sheet.insertRow(rowIndex, row_ref._cells.map(x => zoneDescription));
    const s_e = SPECIAL_CELLS['zone_width'].split('-');
    sheet.mergeCells(`${s_e[0]}${rowIndex}:${s_e[1]}${rowIndex}`);
    for (const i in row_ref._cells) {
        new_row._cells[i].style = row_ref._cells[i].style;
    }
    new_row.height = row_ref.height;
    return rowIndex + 1;
}


function getXLSXTemplate(url, sheetName) {
    return fetch(url)
        .then(response => checkStatus(response) && response.arrayBuffer())
        .then(buffer => {
            const workbook = new ExcelJS.Workbook();
            workbook.creator = 'Thomas Ducrot (calculator.ovh)';
            workbook.company = 'OVHCloud';
            return workbook.xlsx.load(buffer);
        })
        .then(file => file.getWorksheet(sheetName))
}

function checkStatus(response) {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - ${response.statusText}`);
    }
    return response;
}