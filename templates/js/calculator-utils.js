const COORDINATES_TO_SAVE_FORMULA = [
    'J20','J21','J22','J23','J24','J25','J27','J28','J29','J30'
];
const SPECIAL_CELLS = {
    'conformity': 'A2',
    'link': 'M2',
    'subsidiary_description': 'B6',
    'price_formated_cells': ['E17', 'F17', 'J17'],
    'client': 'B10',
    'client_2': 'D10',
    'author': 'G7',
    'zone_width': 'A-J',
    'item_width': 'A-D',
    'row_ref_zone': 16,
    'row_ref_item': 17,
    'currency_symbol': 'C5',
    'currency': 'C6',
    'tax_name': 'C7', 'tax_rate': 'C8',
    'support_name': 'C9', 'support_percent': 'C10', 'support_min': 'C11',
    'exceptionnal_discount': 'C12',
    'budget_duration': 'C13',
    'legal_start': 'A62'
};
const SUPPORT_KEY_TO_NAME = {'f': 'entreprise', 'e': 'entreprise', 'b': 'business', 's': 'standard'};
const PREFIX_LEGAL_TEXT = {
    'fr': 'Conditions Particulières',
    'en': 'Special Condition',
    'de': 'Besonderen Bedingungen '
};
const PREFIX_ZONE_TEXT = 'Zone ';
const TEMPLATE_VERSION = 1;

const num_format = (symbol) => `_ # ##0.00" ${symbol}";- # ##0.00" ${symbol}";_ "";`;
const price_formula = (row) => `F${row}*G${row}*(1-I${row})`;
const cell_vertical_offset = (coord, offset) => coord.replace(/([A-Z]+)([0-9]+)/g, (m,col,row)=>`${col}${parseInt(row)+offset}`);

function getItemRowHeightFromDescription(description) {
    return description.split('\n').length * 10 * 1.4;
}

function DC_key_to_text(key) {
    return `${DCS[key].city} (${DCS[key].country})`;
}

function getItem(key, quantity, commit, discount) {
    let defaultQuantity = 1;
    console.log(key);
    if (index[key].description.includes('DB')) {
        const match = index[key].description.match(/([0-9]) node/);
        if (match.length == 2) {
            defaultQuantity = parseInt(match[1]);
        }
    }

    let item = {
        key: key,
        description: index[key].description,
        setupfee: index[key].setupfee || 0,
        pricePerUnit: pricekey in index[key] ? index[key][pricekey] : index[key].price,
        quantity: quantity || defaultQuantity,
        commit: commit || 1,
        discount: discount || 0,
    };
    let setupFee = item['setupfee'] * item.quantity;
    if (item.key.startsWith('b-') && item.commit >= 6) {
        setupFee = 0;
        item['setupfee'] = 0
    }
    item.setupfee = setupFee;

    item['total'] = item['pricePerUnit'] * item.quantity * (1 - (item.discount) / 100);
    return item;
}

function saveXLSX(state) {
    if (state.zones.length == 0 || state.zones[0].items.length == 0) {
        return;
    }
    const date = new Date().toISOString().split('T')[0];
    const currency_name = CURRENCY in CURRENCIES ? CURRENCIES[CURRENCY]['name'] : CURRENCY;

    getXLSXTemplate(XLSX_TEMPLATE.replace('template', `template_${state.lang}`), XLSX_SHEETNAME).then(sheet => {
        console.log(sheet.getCell(SPECIAL_CELLS['conformity']).value)
        sheet.getCell(SPECIAL_CELLS['conformity']).value = `${sheet.getCell(SPECIAL_CELLS['conformity']).value} ${(conformity != 'default') ? conformity.toUpperCase() : ''}`;
        console.log(sheet.getCell(SPECIAL_CELLS['conformity']).value)
        
        sheet.getCell(SPECIAL_CELLS['link']).value = {'text': 'Calculator link', 'hyperlink': SerilizeState()};
        sheet.getCell(SPECIAL_CELLS['subsidiary_description']).value = OVH_SUBSIDIARY_ADDRESS[sub] || OVH_SUBSIDIARY_ADDRESS['FR'];
        sheet.getCell(SPECIAL_CELLS['client']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['tax_name']).value = (state.lang == 'fr') ? 'TVA' : 'VAT';
        sheet.getCell(SPECIAL_CELLS['tax_rate']).value = TAX_RATE;
        sheet.getCell(SPECIAL_CELLS['client_2']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['author']).value = state.author;
        sheet.getCell(SPECIAL_CELLS['currency']).value = currency_name;
        sheet.getCell(SPECIAL_CELLS['support_name']).value = SUPPORT_KEY_TO_NAME[state.support];
        sheet.getCell(SPECIAL_CELLS['support_percent']).value = SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].percent;
        sheet.getCell(SPECIAL_CELLS['support_min']).value = state.support == 'f' ? 0 : SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].minimum;

        if (state.totaldiscount > 0) {
            sheet.getCell(SPECIAL_CELLS['exceptionnal_discount']).value = state.totaldiscount;
        }
        for (const cell of SPECIAL_CELLS['price_formated_cells']) {
            sheet.getCell(cell).numFmt = num_format(CURRENCY_SYMBOL);
        }
        for (const cell of COORDINATES_TO_SAVE_FORMULA) {
            sheet.getCell(cell).numFmt = num_format(CURRENCY_SYMBOL);
        }

        // Display legals
        let legal_count = 0;
        for (const key of state.legal_checked.split('')) {
            const text_cell = cell_vertical_offset(SPECIAL_CELLS['legal_start'], legal_count);
            const url_cell = cell_vertical_offset(SPECIAL_CELLS['legal_start'], legal_count+1);
            sheet.getCell(text_cell).value =  PREFIX_LEGAL_TEXT[state.lang] + ' ' + res.legal[state.lang][key].text;
            sheet.getCell(text_cell).style =  {'font': {'bold': true, 'size': 10}};
            sheet.getCell(url_cell).value =  {'text': res.legal[state.lang][key].url, 'hyperlink': res.legal[state.lang][key].url};
            legal_count += 2;
        }

        // Display zones and items
        let offset = -2;
        let row_index = SPECIAL_CELLS.row_ref_item + 1;
        for (const zone of state.zones) {
            if (!zone || !(zone.items) || zone.items.length == 0) {
                continue;
            }
            if (offset < 0) {
                sheet.getCell(`A${row_index - 2}`).value = PREFIX_ZONE_TEXT + DC_key_to_text(zone['key']);
            } else {
                row_index = insertZoneRow(sheet, row_index, PREFIX_ZONE_TEXT + DC_key_to_text(zone['key']))
            }
            offset += 1;
            for (const item of zone['items']) {
                if (!item || Object.keys(item).length == 0) {
                    continue;
                }
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
    .then(buffer => saveByteArray([buffer], `${state.title} v${date}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
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
    // console.log(voffset);
    for (const i in old_coordinates) {
        const new_coord = cell_vertical_offset(old_coordinates[i], voffset);
        const old_formula = sheet.getCell(new_coord).formula || '';
        // regex https://regex101.com/r/SHrdes/1
        const new_formula = old_formula.replace(/(^|[^(])([A-Z]+)([1-9][0-9]*)/g, (m, p0,p1,p2) => `${p0}${p1}${parseInt(p2)+voffset}`);
        // console.log({old: old_coordinates[i], new: new_coord, old_formula: old_formula, new_formula: new_formula})
        sheet.getCell(new_coord).value = {formula: new_formula};
    }
}

function insertPriceRow(sheet, rowIndex, description, installCost, unitCost, quantity, commitDuration, commitDiscount) {
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_item);
    const row_values = [description, null, null, null, installCost, unitCost, quantity, commitDuration, commitDiscount, {formula: price_formula(rowIndex)}];
    const new_row = sheet.insertRow(rowIndex, row_values, 'i');
    const s_e = SPECIAL_CELLS['item_width'].split('-');
    if (`${s_e[0]}${rowIndex}` in sheet._merges) {
        delete sheet._merges[`${s_e[0]}${rowIndex}`];
    }
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
    if (`${s_e[0]}${rowIndex}` in sheet._merges) {
        delete sheet._merges[`${s_e[0]}${rowIndex}`];
    }
    sheet.mergeCells(`${s_e[0]}${rowIndex}:${s_e[1]}${rowIndex}`);
    for (const i in row_ref._cells) {
        new_row._cells[i].style = row_ref._cells[i].style;
    }
    new_row.height = row_ref.height;
    return rowIndex + 1;
}


function getXLSXTemplate(url, sheetName) {
    return fetch(`${url}?v${TEMPLATE_VERSION}`)
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