const ABREV_TOTAL = {
    'title': 't',
    'company': 'b',
    'author': 'a',
    'support': 's',
    'totaldiscount': 'u',
    'legal_checked': 'l',
    'version': 'v'
}

const ABREV_ITEM = {
    'key': 'k',
    'commit': 'c',
    'discount': 'e',
    'quantity': 'q',
}

const ZONE_RE = RegExp('z([A-Z]{3}[0-9]?(?: TZ)?)', 'g');  // https://regex101.com/r/DBE4kb/1
const ITEM_RE = RegExp('k([pqb]-[a-zA-Z0-9]{2})', 'g');

function SerilizeState() {
    let output = `${location.origin}${location.pathname}?con=${conformity}&sub=${sub}`;
    let data = '';
    for (const z of state.zones) {
        let zoneString = `z${z.key}`;
        if(z.items.length === 0) {
            continue;
        }
        for (const i of z.items) {
            if (!(Object.keys(i).length)){ 
                continue;
            }
            zoneString += Object.keys(ABREV_ITEM).map(k => `${ABREV_ITEM[k]}${i[k]}`).join('');
        }
        data += zoneString;
    }


    output += '&' + Object.keys(ABREV_TOTAL).map(k => `${ABREV_TOTAL[k]}=${encodeURIComponent(state[k])}`).join('&');
    output += `&zs=${encodeURIComponent(data)}`;
    if (navigator && navigator.clipboard) {
        navigator.clipboard.writeText(output);
    }
    return output;
}

function buildReverseDict(dict) {
    let reverse_dict = {};
    const keys = Object.keys(dict);
    const values = Object.values(dict);
    for (const i in values) {
        reverse_dict[values[i]] = keys[i];
    }
    return reverse_dict;
}

function DeserializeURI() {
    let reverse_abrev_total = buildReverseDict(ABREV_TOTAL);
    let search = location.search;

    let newstate = { zones: []};
    Object.keys(reverse_abrev_total).forEach((k) => {
        newstate[reverse_abrev_total[k]] = decodeURIComponent(new URLSearchParams(search).get(k) || '');
        if (reverse_abrev_total[k] == 'legal_checked') {
            console.log(newstate[reverse_abrev_total[k]])
            newstate[reverse_abrev_total[k]] = JSON.parse(`[${newstate[reverse_abrev_total[k]]}]`);
        }
    });
    
    search = decodeURIComponent(new URLSearchParams(search).get('zs'));
    const search_zones = search.split(ZONE_RE).slice(1); // Split zones
    // console.log(search_zones);
    for (let i = 0; i < search_zones.length; i+=2) {
        const zoneData = search_zones[i+1].split(ITEM_RE).slice(1);
        console.log(zoneData)
        let items = []
        for (let j=0; j < zoneData.length; j+=2) {  // Split items
            const key = zoneData[j];
            const data = zoneData[j+1];
            const qcd = ['quantity', 'commit', 'discount'].map((x) => {
                return parseInt(data.match(new RegExp(`${ABREV_ITEM[x]}([0-9]+)`))[1]);
            });
            items.push(getItem(key, qcd[0], qcd[1], qcd[2]));
        }
        newstate.zones.push({'key': search_zones[i], 'items': items})
    }

    return newstate;
}