const COORDINATES_TO_SAVE_FORMULA = [
    'J20','J21','J22','J23','J24','J25','J27','J28','J29','J30'
];
const SPECIAL_CELLS = {
    'conformity': 'A2',
    'link': 'L2',
    'subsidiary_description': 'B6',
    'price_formated_cells': ['E17', 'F17', 'J17'],
    'client': 'B10',
    'client_2': 'D10',
    'author': 'G7',
    'zone_width': 'A-J',
    'item_width': 'A-D',
    'row_ref_zone': 16,
    'row_ref_item': 17,
    'currency_symbol': 'M2',
    'currency': 'N2',
    'tax_name': 'O2', 'tax_rate': 'P2',
    'support_name': 'Q2', 'support_percent': 'R2', 'support_min': 'S2',
    'budget_duration': 'T2',
    'exceptionnal_discount': 'U2',
    'legal_commit_text_ref': 'M13',
    'legal_start': 'A43',
    'legal_commit_text_area': 'A44'
};
const SUPPORT_KEY_TO_NAME = {'f': 'entreprise', 'g': 'entreprise', 'e': 'entreprise', 'b': 'business', 'c': 'business', 's': 'standard'};
const PREFIX_ZONE_TEXT = 'Zone ';

const num_format = (symbol) => `_ # ##0.00???" ${symbol}";- # ##0.00???" ${symbol}";_ "";`;
const num_format_2decimals = (symbol) => `_ # ##0.00" ${symbol}";- # ##0.00" ${symbol}";_ "";`;

const price_formula = (row) => `F${row}*G${row}*(1-I${row})`;
const cell_vertical_offset = (coord, offset) => coord.replace(/([A-Z]+)([0-9]+)/g, (m,col,row)=>`${col}${parseInt(row)+offset}`);

function countDecimals (number) {
    if (Math.floor(number) === number) return 0;
    return number.toString().split(".")[1].length || 0; 
}

function getItemRowHeightFromDescription(description) {
    return description.split('\n').length * 10 * 1.4;
}

function DC_key_to_text(key) {
    return `${DCS[key].city} (${DCS[key].country})`;
}

function getItem(key, quantity, commit, discount) {
    let defaultQuantity = 1;
    console.log(key);
    if (index[key].description.includes('DB1')) {
        const match = index[key].description.match(/([0-9]) node/);
        if (match && match.length == 2) {
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
        sheet.getCell(SPECIAL_CELLS['conformity']).value = `${sheet.getCell(SPECIAL_CELLS['conformity']).value} ${(conformity != 'default') ? conformity.toUpperCase() : ''}`;
        sheet.getCell(SPECIAL_CELLS['link']).value = {'text': 'Calculator link', 'hyperlink': SerilizeState()};
        sheet.getCell(SPECIAL_CELLS['subsidiary_description']).value = OVH_SUBSIDIARY_ADDRESS[sub] || OVH_SUBSIDIARY_ADDRESS['FR'];
        sheet.getCell(SPECIAL_CELLS['client']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['tax_name']).value = (state.lang == 'fr') ? 'TVA' : 'VAT';
        sheet.getCell(SPECIAL_CELLS['tax_rate']).value = TAX_RATE;
        sheet.getCell(SPECIAL_CELLS['client_2']).value = state.company;
        sheet.getCell(SPECIAL_CELLS['author']).value = state.author;
        sheet.getCell(SPECIAL_CELLS['currency']).value = currency_name;
        sheet.getCell(SPECIAL_CELLS['currency_symbol']).value = CURRENCY_SYMBOL;
        sheet.getCell(SPECIAL_CELLS['support_name']).value = SUPPORT_KEY_TO_NAME[state.support].toUpperCase();
        sheet.getCell(SPECIAL_CELLS['support_percent']).value = state.support == 'g' ? 15 : SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].percent;
        sheet.getCell(SPECIAL_CELLS['support_min']).value = ['f','g','c'].includes(state.support) ? 0 : SUPPORT[SUPPORT_KEY_TO_NAME[state.support]].minimum;
        if (state.totaldiscount > 0) {
            sheet.getCell(SPECIAL_CELLS['exceptionnal_discount']).value = state.totaldiscount;
        }
        for (const cell of SPECIAL_CELLS['price_formated_cells']) {
            sheet.getCell(cell).numFmt = num_format(CURRENCY_SYMBOL);
        }
        for (const cell of COORDINATES_TO_SAVE_FORMULA) {
            sheet.getCell(cell).numFmt = num_format_2decimals(CURRENCY_SYMBOL);
        }

        // Display legals
        let legal_index = 0;
        let legalIndexStart = parseInt(SPECIAL_CELLS['legal_start'].match(/[0-9]+/)[0])

        let legal_choices = res.legal[state.lang]['mandatory_keys'];
        for (const choice of legal_choices) {
            const txt = choice.title || choice.key;
            insertLegalLink(sheet, legalIndexStart + legal_index, txt, choice.url);
            legal_index += 2;
        }

        legal_choices = res.legal[state.lang]['to_select_keys'];
        for (const key of state.legal_checked) {
            const txt = legal_choices[key].title || legal_choices[key].key;
            insertLegalLink(sheet, legalIndexStart + legal_index, txt, legal_choices[key].url);
            legal_index += 2;
        }

        // Display zones and items
        let max_commit = 1;
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
                if (offset < 0) {  // first row, update the ref row instead of inserting a new row
                    const row = sheet.getRow(row_index - 1);
                    const item_keys = ['description', 'description', 'description', 'description', 'setupfee', 'pricePerUnit', 'quantity', 'commit', 'discount']
                    for (const i in item_keys) {
                        row.getCell(parseInt(i)+1).value = (item_keys[i] == 'discount') ? item[item_keys[i]]/100 : item[item_keys[i]];
                    }
                    row.height = getItemRowHeightFromDescription(item['description']);
                } else {
                    row_index = insertPriceRow(sheet, row_index, item.description, item.setupfee, item.pricePerUnit, item.quantity, item.commit, item.discount/100);
                }
                if (item['commit'] > max_commit) {
                    max_commit = item['commit'];
                }
                offset += 1;
            }
        }
        update_formula(sheet, COORDINATES_TO_SAVE_FORMULA, offset);
        displayCommitLegalText(sheet, offset + legal_index, max_commit);
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

function displayCommitLegalText(sheet, offset, max_commit) {
    console.log(max_commit);
    if (max_commit <= 1) { return; }
    let text = sheet.getCell(SPECIAL_CELLS['legal_commit_text_ref']).value;
    text = text.replace('COMMIT', `${max_commit}`);
    let legal_text_cell = cell_vertical_offset(SPECIAL_CELLS['legal_commit_text_area'], offset);
    sheet.getCell(legal_text_cell).value = text;
    sheet.getCell(legal_text_cell).height = 10 * 1.4 * 6; // 5 lines
}

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

function insertLegalLink(sheet, rowIndex, description, link) {
    const row_ref_desc = sheet.getRow(cell_vertical_offset(SPECIAL_CELLS.legal_start, -2))
    const row_ref_link = sheet.getRow(cell_vertical_offset(SPECIAL_CELLS.legal_start, -1))
    const new_row_desc = sheet.insertRow(rowIndex, [description]);
    const new_row_link = sheet.insertRow(rowIndex+1, [link]);

    new_row_desc.getCell(1).style =  {'font': {'bold': true, 'size': 10, name: 'Arial'}};
    new_row_link.getCell(1).value =  {'text': link, 'hyperlink': link, 'font': {'bold': false, 'size': 10, name: 'Arial'}};

    for (const i in row_ref_desc._cells) {
        new_row_desc._cells[i].style = row_ref_desc._cells[i].style;
        new_row_link._cells[i].style = row_ref_link._cells[i].style;
    }
}

function insertPriceRow(sheet, rowIndex, description, installCost, unitCost, quantity, commitDuration, commitDiscount) {
    console.log([rowIndex, description])
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_item);
    const row_values = [description, null, null, null, installCost, unitCost, quantity, commitDuration, commitDiscount, {formula: price_formula(rowIndex)}];
    const new_row = sheet.insertRow(rowIndex, row_values, 'o');
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
    return fetch(`${url}?v1`)
        .then(response => checkStatus(response) && response.arrayBuffer())
        .then(buffer => {
            const workbook = new ExcelJS.Workbook();
            workbook.creator = 'Thomas Ducrot (pricelist.ovh/calculator.html)';
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