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
    'discout': 'e',
    'quantity': 'q',
    'setupfee': 's',
}

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

const ZONE_RE = RegExp('^[A-Z ]{3,}', 'g');

function DeserializeURI(uri) {
    let reverse_abrev_item = buildReverseDict(ABREV_ITEM);
    let reverse_abrev_total = buildReverseDict(ABREV_TOTAL);
    const search = '?' + uri.split('?')[1]; // location.search

    let rstate = {};
    Object.keys(reverse_abrev_total).forEach((k) => {
        rstate[reverse_abrev_total[k]] = decodeURIComponent(new URLSearchParams(search).get(k));
    });
    
    let zones = {};
    search = new URLSearchParams(search).get('zs');

    // Split zones
    const search_zones = search.replace(/(.)z([A-Z]{3,})/g, (m, p1, p2) => `${p1}\n${p2}`).split('\n');
    search_zones[0] = search_zones[0].slice(1);



    search_zones.map(z => {
        // Split Items
        zoneKey = z.match(ZONE_RE)[0];
        z = z.replace(ZONE_RE, '');
        items = z.replace(/k[pqb]-[a-z]{2}/g, '\n$&').split('\n')
        // TODO
    })


    // decodeURIComponent(search_zones[0]).match(/([A-Z ]{3,})k([pqb]-[a-z]{2})/)
    console.log(rstate);
}

// TEST
// DeserializeURI('http://localhost/calculator.html?con=default&sub=FR&t=mondevi%20pour%20client%2011&b=13098%20%26%20akdfj%20%2F%2F&a=asdfj&s=b&u=0&zs=zSBGkb-aac1e0q1s135.99')
DeserializeURI('http://localhost/calculator.html?con=default&sub=FR&t=&b=&a=&s=b&u=0&zs=zSBGkb-aac1e0q1s135.99kp-aac1e0q1s0zWAWkb-aoc1e0q1s99.99kq-aac1e0q1s0zSBG%20TZkq-abc1e0q1s0kb-a6c1e0q1s1011.99');