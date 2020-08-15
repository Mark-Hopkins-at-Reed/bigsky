'''
input:
[{
    time  :  08:00
    summary  :  Dangerously Windy and Overcast
    icon  :  wind
    precipIntensity  :  0
    precipProbability  :  0
    temperature  :  8.15
    apparentTemperature  :  2.4
    dewPoint  :  4.11
    humidity  :  0.76
    pressure  :  1014.7
    windSpeed  :  39.15
    windGust  :  45.66
    windBearing  :  46
    cloudCover  :  0.97
    uvIndex  :  1
    visibility  :  10
    ozone  :  359.9
    unix_time  :  1589180400
},...
]
output:
{
    now: 3
    times: [[5,7],[12,18]]
    weather: [
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
        }, ...
    ]
}
'''
import bigsky.forecast as fc
import torch

class ForecastLoader:

    def __init__(self):
        self.fors = []
        self.datapoints = []

    def add_dataset(self, file_path):
        f = fc.read_forecast_dir(file_path)
        self.fors += f
        for forecast in f:
            for d in forecast['hourly']['data']:
                self.datapoints.append(d)

    def get_fors(self):
        return self.fors

    def get_datapoints(self):
        return self.datapoints
    
    def search_where(self, predicate):
        """predicate sends an hourly data object to a bool"""
        return ForecastLoader.search_list(self.datapoints, predicate)

    @staticmethod
    def search_list(l, predicate):
        """predicate sends an hourly data object to a bool"""
        result = []
        for d in l:
            if predicate(d):
                result.append(d)
        return result

    @staticmethod
    def from_dirs(dirlist, *dirs):
        fl = ForecastLoader()
        if type(dirlist) == list:
            for f in dirlist:
                fl.add_dataset(f)
        else:
            fl.add_dataset(dirlist)
            for f in dirs:
                fl.add_dataset(f)
        return fl

class Classify:
    def __init__(self):
        self.rainnn = torch.load('rain_classifier.exp.json')
        self.KEY_MAXES = {'precipIntensity': 27.1218, 'precipProbability': 1, 
                            'precipAccumulation': 1.8684, 'temperature': 103.37, 
                            'dewPoint': 85.01, 'humidity': 1, 
                            'pressure': 1038.7, 'windSpeed': 45.23, 
                            'windGust': 78.64, 'cloudCover': 1, 
                            'uvIndex': 14, 'visibility': 10, 
                            'ozone': 472.3}
        self.INTENSITIES = ['extra-light','light','moderate','heavy']


    def precip_intense(self, d):
        def find_max(v):
            maxv = v[0].item()
            maxi = 0
            for i in range(v.shape[0]):
                if v[i].item() > maxv:
                    maxi = i
                    maxv = v[i].item()
            return maxi
        vec = torch.stack([torch.Tensor([1.0]+[d.get(k,0)/self.KEY_MAXES[k] for k in self.KEY_MAXES.keys()])])
        ans = self.rainnn(vec,None)[0]
        return find_max(ans[0])

    def cloud_intense(self, d):
        n = 0
        cc = d['cloudCover']
        if cc > .31:
            n += 1
            if cc > .59:
                n += 1
                if cc > .88:
                    n += 1
        return n

    def wind_intense(self, d):
        if d['windSpeed'] >= 39 or d['windGust'] >= 47:
            return 3
        elif (d['windSpeed'] > 25 or d['windGust'] >= 39) and d['cloudCover']<.31:
            return 1 
        elif (d['windSpeed'] > 25.01 or d['windGust'] >= 38.99) and d['cloudCover']>=.31:
            return 1
        else:
            return 0
    
    def intense_num_to_str(self, x):
        return self.INTENSITIES[x]

    @staticmethod
    def is_precip(d):
        return d['precipProbability'] > .25

    @staticmethod
    def is_cloud(d):
        return d['cloudCover'] > .31

    @staticmethod
    def is_wind(d):
        return d['windSpeed'] > 25 or d['windGust'] >= 39

    @staticmethod
    def is_fog(d):
        return d['visibility'] <= 2

    @staticmethod
    def is_humid(d):
        """This one ain't perfect but its pretty good, ~95% acc over all data"""
        return d['apparentTemperature']-d['temperature'] > 1.5 and d['humidity'] > .8 and not Classify.is_cloud(d)

def bucketvector(d, c):
    # consider making this a method of Classify
    return [c.is_precip(d), 
            c.is_wind(d), 
            c.is_cloud(d) and not c.is_precip(d), 
            c.is_fog(d), 
            c.is_humid(d)]

def guess_summary(d, c):
    words = ['Rain','Wind','Cloud','Fog','Humid']
    v = bucketvector(d, c)
    s = []
    for i in range(len(v)):
        if v[i]:
            s.append(words[i])
    return ' and '.join(s)

def jsonify_hour(d, c):
    """
    Transforms a datapoint object into a closer thing to that json format
    we have:
        time: the time
        accumulation: how much precip has accumulated if any
        weather: a list of objects with (type, degree, probability) as in the target
    """
    ans = {'time': int(d['time'][:2])}
    v = bucketvector(d, c)
    cfns = [c.precip_intense, c.wind_intense, c.cloud_intense, lambda d: 2, lambda d: 2]
    words = ['rain','wind','cloud','fog','humid']
    weather = []
    for i in range(len(v)):
        if v[i]:
            prob = 'high'
            word = words[i]
            if i == 0:
                if d['precipType'] == 'snow':
                    word = 'snow'
                if d['precipProbability'] < .65:
                    prob = 'medium'
            intensity = c.intense_num_to_str(cfns[i](d))
            weather.append({
                'type': word,
                'degree': intensity,
                'probability': prob
            })
    ans['weather'] = weather
    ans['accumulation'] = d.get('accumulation', 0)
    return ans

def listify_from_loader(fl, c=None):
    if c == None:
        c = Classify()
    return [listify_forecast(f, c) for f in fl.get_fors()]

def listify_forecast(forecast, c=None):
    if c == None:
        c = Classify()
    return [jsonify_hour(d, c) for d in forecast['hourly']['data']]

def weather_times(forecast, l=None):
    if l == None:
        l = listify_forecast(forecast)
    times = {
        'rain': [], 'snow': [],
        'cloud':[], 'wind': [],
        'humid':[], 'fog':  []
    }
    for d in l:
        for w in d['weather']:
            times[w['type']].append(d['time'])
    intvldict = dict()
    for word, hours in times.items():
        if hours == []:
            intvldict[word] = []
            continue
        for i in range(1, len(hours)):
            while hours[i-1] >= hours[i]:
                hours[i] += 24
        intvls = []
        start = hours[0]
        last = hours[0]
        for h in hours[1:]:
            if h - last > 1:
                intvls.append([start, last])
                last = h
                start = h
            else:
                last = h
        intvls.append([start,last])
        intvldict[word] = intvls
    nettimedict = dict()
    for word, intvls in intvldict.items():
        z = 0
        for i in intvls:
            z += i[1]-i[0]+1
        nettimedict[word] = z
    return nettimedict, intvldict

def coincident_weather(intvldict, weather_type, weather_time):
    """Will tell me what weather type(s) coincide with the one given"""
    # TODO: don't take weather_time as an arg
    main = intvldict[weather_type]
    ans = []
    for word, intvls in intvldict.items():
        if word == weather_type:
            continue
        total_miss = 0
        for s,t in main:
            miss = t-s
            for i in intvls:
                if i[0] < t and i[1] > s:
                    miss -= (min(i[1],t) - max(i[0],s))
            total_miss += miss
        if total_miss / weather_time < .2: #(say)
            ans.append(word)
    return ans

def avg_weather(js_list, weather_type):
    """Will create an avg of a weather type (i.e. if it goes from heavy to light rain => 'moderate')"""
    pass

def priority_weather(timedict):
    """What is the most important kind of weather today?"""
    if timedict['rain'] > 0:
        return 'rain'
    if timedict['snow'] > 0:
        return 'snow'
    if timedict['wind'] > 0:
        return 'wind'
    if timedict['cloud'] > 0:
        return 'cloud'
    if timedict['fog'] > 0:
        return 'fog'
    if timedict['humid'] > 0:
        return 'humid'
    return 'clear'

def accumulate(js_list):
    """Figures out how much precip has accumulated. Should be an easy sum"""
    pass

def forecast2json(forecast):
    """
    Will put this all together:
    1. Listify to basic json                                    READY
        - this is where all the bucketing happens
    2. Translate to times                                       READY
    3. Prioritize to find most important                        READY
    4. look for coincidences                                    READY
    5. Prioritize for most important coincidence                READY
    6. Average dominant weather
    7. Average coincident weather
    8. Find net accumulation
    9. ANS = {
        now: # first hour
        times: # intvldict[weather_type] from <2>,<3>
        weathers: [
            {result of <6>, measure = accumulation from <8>},
            {result of <7>}
        ]
        snow_chance: low temp? accumulation > 0? Unsure...
    }
    """
    pass