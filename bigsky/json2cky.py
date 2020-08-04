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

There is no longer such thing as a "heavy drizzle" or a "light rain". Same goes for the snow variants.
Instead, "heavy drizzle" is just "rain" and "light rain" is "drizzle".
I'm not sure if that is going to be a problem? The CFG can generate these things, but idk if we see them.
I believe that the CFG does overgenerate a bit.

Again, this is hardcoded given the CFG. So this stuff should be highly open to change
'''

def treeify_measure(js):
    hi, lo = js['max'], js['min']
    if lo == 0:
        # only want a ~ for low error and also not something like "(n) - (n+1)"
        return ['MEASURE', 
                '&lt;', 
                ['NUM', str(round(hi))], 
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
    if deg == 'heavy' or deg == 'light':
        mods.append(deg)
    if len(mods) == 1:
        result.append(['PRECIPMODIFIERS', ['PRECIPMODIFIER', mods[0]]])
    elif len(mods) == 2:
        result.append(['PRECIPMODIFIERS', 
                        ['PRECIPMODIFIER', mods[0]], 
                        ['PRECIPMODIFIERS', ['PRECIPMODIFIER', mods[1]]]
                    ])    
    noun = ('drizzle' if typ == 'rain' else 'flurries') if deg == 'extra-light' else typ
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

TIME_LABELS = [
    (0, 5,   'night'),
    (5, 12,  'morning'),
    (12, 17, 'afternoon'),
    (17, 22, 'evening'),
    (22, 24, 'night')    
]

def stringify_hour(hr):
    while hr > 24:
        hr -= 24
    ans = []
    for k in TIME_LABELS:
        if hr <= k[1] and hr >= k[0]:
            ans.append(k[2])
    return ans

def treeify_interval(intvl, now):
    '''
    Interval => CKY Time tree
    e.g.
    [5,12] =>  ['TIME', ['BTIME', 'tomorrow', ['TIMEWORD', start]]]
    '''
    start  = stringify_hour(intvl[0])[-1]
    end    = stringify_hour(intvl[1])[0]
    nowstr = stringify_hour(now)[-1]
    ans = []
    if start == end and not intvl[1] - intvl[0] > 7:
        if intvl[0] > 29:
            ans = ['TIME', ['BTIME', 'tomorrow', ['TIMEWORD', start]]]
        elif intvl[0] == now:
            if start != 'night':
                ans = ['TIME', 'until', ['BTIME', 'later', 'this', start]]
            else:
                ans = ['TIME', 'until', ['BTIME', 'later', 'tonight']]
        elif start == nowstr:
            if start != 'night':
                ans = ['TIME', ['BTIME', 'later', 'this', start]]
            else:
                ans = ['TIME', ['BTIME', 'later', 'tonight']]
        else:
            ans = ['TIME',['BTIME', 'in', 'the', ['TIMEWORD', start]]]
    else:
        if intvl[0] == now:
            if intvl[1] > 29:
                ans = ['TIME', 'until', ['BTIME', 'tomorrow', ['TIMEWORD', end]]]
            elif end != 'night':
                ans = ['TIME', 'until', ['BTIME', 'this', ['TIMEWORD', end]]]
            else:
                ans = ['TIME', 'until', ['BTIME', 'tonight']]
        elif start == nowstr:
            if intvl[1] > 29:
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'this', start], ',',
                            'continuing', 'until', ['BTIME', 'tomorrow', ['TIMEWORD', end]]]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'tomorrow', ['TIMEWORD', end]]]
            elif end != 'night':
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'this', start], ',',
                            'continuing', 'until', ['BTIME', 'this', ['TIMEWORD', end]]]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'this', ['TIMEWORD', end]]]
            else:
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'this', start], ',',
                            'continuing', 'until', ['BTIME', 'tonight']]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'later', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'later', 'tonight']]
        elif intvl[0] < 29:
            if intvl[1] > 29:
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'this', ['TIMEWORD', start]], ',',
                            'continuing', 'until', ['BTIME', 'tomorrow', ['TIMEWORD', end]]]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'tomorrow', ['TIMEWORD', end]]]
            elif end != 'night':
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'this', ['TIMEWORD', start]], ',',
                            'continuing', 'until', ['BTIME', 'this', ['TIMEWORD', end]]]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'this', ['TIMEWORD', end]]]
            else:
                if start != 'night':
                    ans = ['TIME', 'starting', ['BTIME', 'this', ['TIMEWORD', start]], ',',
                            'continuing', 'until', ['BTIME', 'tonight']]
                else:
                    ans = ['TIME', 'starting', ['BTIME', 'tonight'], ',',
                            'continuing', 'until', ['BTIME', 'later', 'tonight']]
        else:
            ans = ['TIME', ['BTIME', 'tomorrow']]
    return ans

def treeify_time(intervals, now):
    if len(intervals) == 0:
        raise ValueError("No time intervals provided")
    #first condense the intervals so that there is no overlapping
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals))[::-1]:
        s, t = intervals[i-1], intervals[i]
        if s[1] >= t[0]:
            s[1] = max(s[1],t[1])
            intervals.pop(i)
    # case 1: just one interval. is hopefully most cases
    if len(intervals) == 1:
        return treeify_interval(intervals[0], now)
    # case 2: 2+ intervals, first starts now. "until ZZZ, starting again YYY"
    elif intervals[0][0] == now:
        time_start = treeify_interval(intervals[0], now)
        time_end = treeify_interval(intervals[1], now)
        for t in time_end:
            if type(t) == list and t[0] == 'BTIME':
                return time_start + [',', 'starting', 'again', t]
        raise ValueError("Something went wrong; {} has no BTIME".format(time_end))
    # case 3: everything is tomorrow
    elif intervals[0][0] >= 29:
        return ['TIME',['BTIME', 'tomorrow']]
    # else: 2+ intervals, not starting now
    else:
        trees = [treeify_interval(intvl, now) for intvl in intervals]
        ans = ['TIME', trees[0], 'and', trees[1]]
        for i in range(2, len(trees)):
            if intervals[i][0] >= 29:
                return ['TIME', ans, 'and', ['TIME',['BTIME', 'tomorrow']]]
            ans = ['TIME', ans, 'and', trees[i]]
        return ans


def treeify(js):
    return ['S', treeify_weather(js['weather']), treeify_time(js['time'], js['now']), '.']

def stringify_tree(tree):
    result = ''
    for w in tree[1:]:
        if type(w) == str:
            result += w + ' '
        else:
            result += stringify_tree(w)
    return result.replace(' ,',',').replace(' . ','.').replace('( ','(').replace(' )',')')