const ExcelJS = require('exceljs');


const COORDINATES_TO_SAVE_FORMULA = [
    'J20','J21','J22','J23','J24','J25','J26','J27',//'J28'
];
const SPECIAL_CELLS = {
    'zone_width': 'A-J',
    'item_width': '',
    'row_ref_zone': 16,
    'row_ref_item': 17,
    'currency': 'A6',
    'taxe_name': 'A7', 'taxe_rate': 'A8',
    'support_name': 'A9', 'support_percent': 'A10', 'support_min': 'A11',
    'exceptionnal_discount': 'A12',
    'budget_duration': 'A13',
};

const price_formula = (row) => `F${row}*G${row}*(1-I${row})`;
const cell_vertical_offset = (coord, offset) => coord.replace(/([A-Z]+)([0-9]+)/g, (m,col,row)=>`${col}${parseInt(row)+offset}`);

// Add a vertical offset to all saved_formulas
function update_formula(sheet, old_coordinates, voffset) {
    for (const i in old_coordinates) {
        const new_coord = cell_vertical_offset(old_coordinates[i], voffset);
        const old_formula = sheet.getCell(new_coord).formula;
        // regex https://regex101.com/r/SHrdes/1
        const new_formula = old_formula.replace(/(^|[^(])([A-Z]+)([1-9][0-9]*)/g, (m, p0,p1,p2) => `${p0}${p1}${parseInt(p2)+voffset}`);
        sheet.getCell(new_coord).value = {formula: new_formula};
    }
}

function insertPriceRow(sheet, rowIndex, description, installCost, unitCost, quantity, commitDuration, commitDiscount) {
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_item);
    // console.log(row_ref._cells.map(x=>x._mergeCount));
    // console.log(row_ref._cells[1]);
    const row_values = [description, description, description, description, installCost, unitCost, quantity, commitDuration, commitDiscount, {formula: price_formula(rowIndex)}];
    const new_row = sheet.insertRow(rowIndex, row_values, 'i');
    // for (const i in row_ref._cells) {
    //     new_row._cells[i].style = row_ref._cells[i].style;
    // }
    new_row.height = description.split('\n').length * row_ref._cells[0].style.font.size * 1.4;
    return rowIndex + 1;
}

function insertZoneRow(sheet, rowIndex, zoneDescription) {
    const row_ref = sheet.getRow(SPECIAL_CELLS.row_ref_zone);
    const new_row = sheet.insertRow(rowIndex, row_ref._cells.map(x => zoneDescription), 'i');
    const s_e = SPECIAL_CELLS['zone_width'].split('-');
    // sheet.mergeCells(`${s_e[0]}${rowIndex}:${s_e[1]}${rowIndex}`);
    // for (const i in row_ref._cells) {
    //     new_row._cells[i].style = row_ref._cells[i].style;
    // }
    new_row.height = row_ref.height;
    return rowIndex + 1;
}

async function main() {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile('template.xlsx');
    workbook.creator = 'Thomas Ducrot tdr2d';
    workbook.company = 'OVHCloud';
    const sheet = workbook.getWorksheet('feuille1');

    let row_index = SPECIAL_CELLS.row_ref_item + 1;
    let offset = 0;

    for (let i = 0; i < 1; i++) {
        row_index = insertPriceRow(sheet, row_index, 'Hôte Additionnel PRE 384 SNC', 0, 1319, 1, '36 mois', 0.15);
        // row_index = insertPriceRow(sheet, row_index, 'Hôte Additionnel PRE 384 SNC\n  desc 1 \n desc 2', 0, 1319, 1, '24 mois', 0.10);
        // row_index = insertZoneRow(sheet, row_index, 'Zone de confiance - France - SBG')
        offset += 1;
    }

    update_formula(sheet, COORDINATES_TO_SAVE_FORMULA, offset);
    await workbook.xlsx.writeFile('tmp.xlsx');
}

main().then(function(){
    console.log('DONE')
}, function(err) {
    console.error(err)
})