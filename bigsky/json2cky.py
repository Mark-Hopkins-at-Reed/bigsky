'''
input looks like this
{
    type: "cloud/wind/rain/snow/fog/humid", 
    degree: "heavy/moderate/light"
    probability: "high/medium/low"
    measure: {
        amt: #number
        unit: "in./cm."
        error: #number
    }
    snow_chance: bool
}

output should look like this
[WEATHER,
    [PRECIP,
        [PRECIPMODIFIERS, [PRECIPMODIFIER "heavy"]], 
        [PRECIPNOUN, "rain"], 
        [PRECIPPAREN, 
            [MEASUREMENT, 
                "(",
                [MEASURE, "&lt;" [NUM, "4"], [UNIT, "in."]],
                ")"
            ]
        ]
    ]
]
or 
[WEATHER, "mostly", "cloudy"]
'''

def treeify_measure(js):
    amt, err = js['amt'], js['error']
    lo = amt - err
    hi = amt + err
    if err <= .5 and abs(round(hi)-hi) <= .001 and abs(round(lo)-lo) <= .001:
        return ['MEASURE', 
                '&lt;', 
                ['NUM', str(round(amt))], 
                ['UNIT', js['unit']]
            ]
    else:
        return ['MEASURE', 
                ['NUM', str(round(lo))], 
                '–', 
                ['NUM', str(round(hi))], 
                ['UNIT', js['unit']]
            ]

def treeify_precip(js):
    deg, typ, prb, snow, meas = js['degree'], js['type'], js['probability'], js['snow_chance'], js['measure']
    result = ['PRECIP']
    mods = []
    if prb == 'medium':
        mods.append('possible')
    if deg != 'moderate':
        mods.append(deg)
    if len(mods) == 1:
        result.append(['PRECIPMODIFIERS', ['PRECIPMODIFIER', mods[0]]])
    elif len(mods) == 2:
        result.append(['PRECIPMODIFIERS', 
                        ['PRECIPMODIFIER', mods[0]], 
                        ['PRECIPMODIFIERS', ['PRECIPMODIFIER', mods[1]]]
                    ])    
    noun = ('drizzle' if typ == 'rain' else 'flurries') if deg == 'light' else typ
    result.append(['PRECIPNOUN', noun])
    if meas == 'UNKNOWN':
        return result  
    m_tree = treeify_measure(meas)
    if snow:
        result.append(['PRECIPPARENS', 
                        ['CHANCEOFSNOW', "(", "with", "a", "chance", "of", m_tree, "of", "snow", ")"]
                    ])
    else:
        result.append(['PRECIPPARENS', 
                        ['MEASUREMENT', "(", m_tree, ")"]
                    ])
    return result

def treeify_weather(js):
    t = js['type']
    if t in "rain$snow":
        return ['WEATHER', treeify_precip(js)]
    elif t == 'wind':
        if js['degree'] == 'heavy':
            return ['WEATHER', 'dangerously', 'windy']
        else:
            return ['WEATHER', 'windy']
    elif t == 'cloud':
        if js['degree'] == 'heavy':
            return ['WEATHER', 'overcast']
        elif js['degree'] == 'moderate':
            return ['WEATHER', 'mostly', 'cloudy']
        else:
            return ['WEATHER', 'partly', 'cloudy']
    elif t == 'fog':
        return ['WEATHER', 'foggy']
    elif t == 'humid':
        return ['WEATHER', 'humid']
    elif t == 'clear':
        return ['WEATHER', 'clear']
    else:
        raise ValueError(t, 'is not a supported kind/name of weather')