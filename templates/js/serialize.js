const ABREV_TOTAL = {
    'title': 't',
    'company': 'b',
    'author': 'a',
    'support': 's',
    'totaldiscount': 'u',
}

const ABREV_ITEM = {
    'key': 'k',
    'commit': 'c',
    'discount': 'e',
    'quantity': 'q',
}

const ZONE_RE = RegExp('z([A-Z ]{3,})', 'g');
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
            zoneString += Object.keys(ABREV_ITEM).map(k => `${ABREV_ITEM[k]}${i[k]}`).join('');
        }
        data += zoneString;
    }

    output += '&' + Object.keys(ABREV_TOTAL).map(k => `${ABREV_TOTAL[k]}=${encodeURIComponent(state[k])}`).join('&');
    output += `&zs=${encodeURIComponent(data)}`;
    console.log(output);
    return output;
}

function buildReverseDict(dict) {
    let reverse_dict = {};
    const keys = Object.keys(dict).sort();
    const values = Object.values(dict).sort();
    for (const i in values) {
        reverse_dict[values[i]] = keys[i];
    }
    return reverse_dict;
}

function DeserializeURI(uri) {
    let reverse_abrev_total = buildReverseDict(ABREV_TOTAL);
    let search = '?' + uri.split('?')[1]; // location.search

    let newstate = {zones: []};
    Object.keys(reverse_abrev_total).forEach((k) => {
        newstate[reverse_abrev_total[k]] = decodeURIComponent(new URLSearchParams(search).get(k));
    });
    
    search = decodeURIComponent(new URLSearchParams(search).get('zs'));
    const search_zones = search.split(ZONE_RE).slice(1); // Split zones
    for (let i = 0; i < search_zones.length; i+=2) {
        const zoneData = search_zones[i+1].split(ITEM_RE).slice(1);
        let items = []
        for (let j=0; j < zoneData.length; j+=2) {  // Split items
            const key = zoneData[j];
            const data = zoneData[j+1];
            const qcd = ['quantity', 'commit', 'discount'].map((x) => {
                return data.match(new RegExp(`${ABREV_ITEM[x]}[0-9]{1,4}`, 'g'))[0];
            });
            items.push(getItem(key, qcd[0], qcd[1], qcd[2]));
        }
        newstate.zones.push({'key': search_zones[i], 'items': items})
    }

    console.log(newstate);
    return newstate;
}

// TEST
// DeserializeURI('http://localhost/calculator.html?con=default&sub=FR&t=mondevi%20pour%20client%2011&b=13098%20%26%20akdfj%20%2F%2F&a=asdfj&s=b&u=0&zs=zSBGkb-aac1e0q1')
// DeserializeURI('http://localhost/calculator.html?con=default&sub=FR&t=&b=&a=&s=b&u=0&zs=zSBGkb-aac1e0q1kp-aac1e0q1zWAWkb-aoc1e0q1kq-aac1e0q1zSBG%20TZkq-abc1e0q1kb-a6c1e0q1');