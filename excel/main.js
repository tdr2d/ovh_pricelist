const ExcelJS = require('exceljs');


let ROW_REF_ZONE = 16;
let ROW_REF_PRICE = ROW_REF_ZONE + 1;
let zone_ranges = [{from: ROW_REF_PRICE, to: ROW_REF_PRICE+1}];
const COORDINATES_TO_SAVE_FORMULA = [
    'J20','J21','J22','J23','J24','J25','J26','J27','J28'
];
const SPECIAL_CELLS = {
    'currency': 'A6',
    'taxe_name': 'A7', 'taxe_rate': 'A8',
    'support_name': 'A9', 'support_percent': 'A10', 'support_min': 'A11',
    'exceptionnal_discount': 'A12',
    'budget_duration': 'A13',
};

const price_formula = (row) => `F${row}*G${row}*(1-I${row})`;
const split_coord = (coord) => coord.match(/([A-Z]+)([0-9]+)/)
const cell_vertical_offset = (coord, offset) => coord.replace(/([A-Z]+)([0-9]+)/g, (m,col,row)=>`${col}${parseInt(row)+offset}`);

function insertPriceRow(sheet, zoneRange, description, installCost, unitCost, quantity, commitDuration, commitDiscount) {
    const row_ref = sheet.getRow(ROW_REF_PRICE+1);
    const row_values = [description, null, null, null, installCost, unitCost, quantity, commitDuration, commitDiscount, {formula: price_formula(zoneRange.to - 1)}];
    const new_row = sheet.insertRow(zoneRange.to - 1, row_values, 'i');
    
    // set style
    for (const i in row_ref._cells) {
        new_row._cells[i].style = row_ref._cells[i].style
    }
    new_row.height = description.split('\n').length * row_ref._cells[0].style.font.size * 1.4;
}

function insertZone(sheet, zoneDescription, rowIndex) {
    const row_ref = sheet.getRow(ROW_REF_ZONE+1);
    const new_row = sheet.insertRow(rowIndex, [zoneDescription], 'i');
    
    // set style
    for (const i in row_ref._cells) {
        new_row._cells[i].style = row_ref._cells[i].style
    }
    new_row.height = row_ref._cells[0].style.font.size;

    return {from: rowIndex, to: rowIndex+1}
}


function update_zone_ranges(zone_ranges, indexZoneWhereNewRow) {
    for (const i in zone_ranges) {
        if (i == indexZoneWhereNewRow) {
            zone_ranges[i].to += 1;
        } else if (i > indexZoneWhereNewRow) {
            zone_ranges[i].from += 1;
            zone_ranges[i].to += 1;
        }
    }
    return zone_ranges;
}

// Add a vertical offset to all saved_formulas
function update_formula(sheet, old_coordinates, voffset) {
    for (const i in old_coordinates) {
        const coord = old_coordinates[i];
        const new_coord = cell_vertical_offset(coord, voffset);
        const old_formula = sheet.getCell(new_coord).formula;
        // regex https://regex101.com/r/SHrdes/1
        const new_formula = old_formula.replace(/(^|[^(])([A-Z]+)([1-9][0-9]*)/g, (m, p0,p1,p2) => `${p0}${p1}${parseInt(p2)+voffset}`);
        sheet.getCell(new_coord).value = {formula: new_formula};
        // console.log([old_formula, new_formula])
    }
}

async function main() {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile('template.xlsx');
    const sheet = workbook.getWorksheet('feuille1');

    let offset = 0
    console.log(zone_ranges);
    insertPriceRow(sheet, zone_ranges[0], 'Hôte Additionnel PRE 384 SNC', 0, 1319, 1, null, null);
    zone_ranges = update_zone_ranges(zone_ranges, 0);
    console.log(zone_ranges);

    insertPriceRow(sheet, zone_ranges[0], 'Hôte Additionnel PRE 384 SNC', 0, 1319, 1, '36 mois', 0.15);
    zone_ranges = update_zone_ranges(zone_ranges, 0);
    console.log(zone_ranges);

    insertPriceRow(sheet, zone_ranges[0], 'Hôte Additionnel PRE 384 SNC\n  desc 1 \n desc 2', 0, 1319, 1, '24 mois', 0.10);
    zone_ranges = update_zone_ranges(zone_ranges, 0);
    console.log(zone_ranges);

    offset = 3;
    update_formula(sheet, COORDINATES_TO_SAVE_FORMULA, offset);
    // sheet.insertRow(19, [1, 'John Doe',new Date(1970,1,1)], 'i');
    
    
    await workbook.xlsx.writeFile('tmp.xlsx');
}

main().then(function(){
    console.log('DONE')
}, function(err) {
    console.error(err)
})