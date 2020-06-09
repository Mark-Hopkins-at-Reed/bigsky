from data import DataManager
import pandas as pd
from collections import defaultdict

#join on: PLT_CN, INVYR, STATECD

#Y var of interest: FORTYPCD

#X vars in RESPONSE: aspect, slope, lat_public, long_public, elev_public
#X vars in SPATIAL: FIAstrat (but don't use), forgrp, forprob, ekd11, demLF, evtLF, forbio
# take cosine and sine of aspect

def bucket_forest_types(x):
    if x == 0 or x == 999:
        result = -1
    elif x >= 180 and x <= 185:
        result = 1 # pinyon juniper
    elif x > 0 and x < 400:
        result = 0 # softwood
    else:
        result = 0 # hardwood
        
    return result    
 
class InteriorWestData:
    
    def __init__(self, df, buckets = bucket_forest_types):
        self.domain = dict()
        self.dtype = dict()
        df.insert(0, "OFFSET", 1.0)
        df["FORTYPCD"] = [buckets(x) for x in df["FORTYPCD"]]
        df = df.loc[df['FORTYPCD'] >= 0]
        self.df = df
        
        categorical_vars = ["FORTYPCD", "forgrp"]
        numeric_vars = ['OFFSET', 'ASPECT', 'SLOPE', 'LAT_PUBLIC', 
                        'LON_PUBLIC', 'ELEV_PUBLIC', "demLF","nlcd11",
                        "forprob", "evtLF","forbio"]
        vartypes = {v: 'categorical' for v in categorical_vars}
        vartypes.update({v: 'numeric' for v in numeric_vars})
        self.mgr = DataManager(self.df, vartypes)
        

    def select_response(self, column):
        return self.mgr.select_response(column)
        
    def select(self, columns):
        return self.mgr.select(columns)
            
    def __len__(self):
        return len(self.df)

    def latitude_buckets(self, interval):
        buckets = defaultdict(list)
        for row_index in range(len(self.df)):
            row = self.df.iloc[row_index]
            latitude = row['LAT_PUBLIC']
            buckets[int(latitude // interval)].append(row_index)
            buckets[int(latitude // interval + interval)].append(row_index)
        return dict(buckets)

    def lat_long_buckets(self, interval):
        lat_buckets = self.latitude_buckets(interval)
        buckets = defaultdict(list)
        for bucket in lat_buckets:
            for row_index in lat_buckets[bucket]:
                row = self.df.iloc[row_index]
                longitude = row['LON_PUBLIC']
                buckets[(bucket, int(longitude // interval))].append(row_index)
                buckets[(bucket, int(longitude // interval + interval))].append(row_index)
        return dict(buckets)

    def all_pairwise_distances(self):
        dists = dict()
        for row1 in range(len(self.df)):
            for row2 in range(row1 + 1, len(self.df)):
                dists[(row1, row2)] = self.distance(self.df.iloc[row1], self.df.iloc[row2])
        return dists
           
    def distance(self, row1, row2):
        squared_long_diff = (row1['LON_PUBLIC'] - row2['LON_PUBLIC']) ** 2
        squared_lat_diff = (row1['LAT_PUBLIC'] - row2['LAT_PUBLIC']) ** 2
        return (squared_long_diff + squared_lat_diff) ** 0.5
        
iwest_data = InteriorWestData(pd.read_csv('plot_level/plt_spatial.csv'))
