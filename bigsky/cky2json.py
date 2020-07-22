from bigsky.cky import make_trees
import json

def flatten_mods(subtree):
    '''Turns a PRECIPMODIFIER tree into a stright list'''
    mods = []
    x = subtree
    while len(x) == 3:
        mods.append(x[1][1])
        x = x[2]
    mods.append(x[1][1])
    return mods

def flatten_parens(subtree):
    '''Gets the important info out of a parenthetical'''
    result = {'snow_chance': subtree[1][0] == 'CHANCEOFSNOW'}
    x = None
    for y in subtree[1]:
        if type(y) == list:
            x = y
            break
    measure = { 'unit': "".join(x[-1][1:]) }
    if len(x) == 5:
        measure['amt'] = (int(x[3][1]) + int(x[1][1]))/2
        measure['error'] = (int(x[3][1]) - int(x[1][1]))/2
    else:
        measure['amt'] = int(x[2][1])
        measure['error'] = .5
    result['measure'] = measure
    return result

def precip_expand(t):
    '''4 kinds of PRECIP phrases, from tree -> dict'''
    if t[1][0] == 'PRECIPMODIFIERS':
        if len(t) == 4:
            return {'modifiers': flatten_mods(t[1]),
                    'noun': t[2][1],
                    'parens': flatten_parens(t[3])}
        else:
            return {'modifiers': flatten_mods(t[1]),
                    'noun': t[2][1]}
    else:
        if len(t) == 3:
            return {'modifiers': [],
                    'noun': t[1][1],
                    'parens': flatten_parens(t[2])}
        else:
            return {'modifiers': [],
                    'noun': t[1][1]}

def find_weather_types(tree):
    '''returns a list of all the WEATHER phrases in the sentence.
       PRECIPs are dicts, everything else is a string
    '''
    if tree[0] == 'S':
        return find_weather_types(tree[1])
    if tree[0] == 'WEATHER' and tree[1][0] == 'WEATHER':
        return find_weather_types(tree[1]) + find_weather_types(tree[3])
    elif tree[0] == 'WEATHER' and tree[1][0] == 'PRECIP':
        return [precip_expand(tree[1])]
    elif tree[0] == 'WEATHER':
        return [" ".join(tree[1:])]
    else:
        # should not get here
        return ["uhhhhh"]

def mold_weather(w):
    ''' Take a WEATHER thingy as created from the tree in the above stuff, 
        turn it into a dict of the form:
            {
                type: "something", 
                degree: "heavy/moderate/light"
                probability: "high/medium/low"
                measure: {
                    amt: #number
                    unit: "in./cm."
                    error: #number
                }
                snow_chance: bool
            }
    '''
    ans = {}
    if type(w) == dict:
        ans['type'] = 'snow' if w['noun'] in 'snow$flurries' else 'rain'
        intensity = 0 if w['noun'] in 'rain$snow' else -1
        probability = False
        for m in w['modifiers']:
            if m == 'heavy':
                intensity += 1
            elif m == 'light':
                intensity -= 1
            elif m == 'possible':
                probability = True
        ans['degree'] = ('heavy' if intensity > 0 else 
                            ('light' if intensity < 0 else 
                                'moderate'))
        ans['probability'] = 'medium' if probability else 'high'
        ans['measure'] = w.get('parens', {}).get('measure', "UNKNOWN")
        ans['snow_chance'] = w.get('parens', {}).get('snow_chance', False)

    elif type(w) == str:
        if 'cloud' in w or w == 'overcast':
            ans['type'] = 'cloud'
            ans['degree'] = ('heavy' if w == 'overcast' else 
                                ('moderate' if w.startswith('mostly') else 
                                    'light'))
        elif 'windy' in w:
            ans['type'] = 'wind'
            ans['degree'] = 'heavy' if w.startswith('danger') else 'light'
        elif w == 'foggy':
            ans['type'] = 'fog'
            ans['degree'] = 'moderate'
        elif w == 'humid':
            ans['type'] = 'humid'
            ans['degree'] = 'moderate'
        elif w == 'clear':
            ans['type'] = 'clear'
            ans['degree'] = 'N/A'
        ans['probability'] = 'high'
        ans['measure'] = 'N/A'
        ans['snow_chance'] = False
    return ans

def jsonify_tree(tree):
    '''Turn a debinarized tree from the weather.cfg CFG into more data-friendly json'''
    weather = find_weather_types(tree)
    weather_json = [mold_weather(w) for w in weather]
    return weather_json
    
def extract_from_sentence(sentence, grammar, cnf_grammar=None):
    '''Turn a NL weather report into possible data-friendly json interpretations'''
    trees = make_trees(sentence, grammar, cnf_grammar)
    print(len(trees))
    return [jsonify_tree(t) for t in trees]