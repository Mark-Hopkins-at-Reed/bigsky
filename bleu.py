from bigsky.forecast2json import compare_end2end, ForecastLoader
import sacrebleu
from data.datapaths import TEST_DIRS

def maybe_generate_forecasts(e2e):
    if e2e == None:
        fl = ForecastLoader.from_dirs(TEST_DIRS)
        forecasts = fl.get_fors()
        print('------ LOADED FORECASTS ------')
        e2e = [compare_end2end(f) for f in forecasts]
    return e2e
    

def exact(e2e=None):
    e2e = maybe_generate_forecasts(e2e)
    results = [ x[0] for x in e2e]
    ct_right = 0
    for b in results:
        if b:
            ct_right += 1
    return ct_right / len(e2e)

def bleu(e2e=None):
    e2e = maybe_generate_forecasts(e2e)
    golds = [x[2] for x in e2e]
    predictions = [x[1] for x in e2e]
    ## Yay list comprehensions!!!
    result = sacrebleu.corpus_bleu(predictions, [golds])
    return result.score

def main(test_dirs=None):
    print('------ LOADIN FORECASTS ------')
    if test_dirs == None:
        fl = ForecastLoader.from_dirs(TEST_DIRS)
    else:
        fl = ForecastLoader.from_dirs(test_dirs)
    forecasts = fl.get_fors()
    print('------ LOADED FORECASTS ------\n')
    e2e = [compare_end2end(f) for f in forecasts]
    print('------ MADE PREDICTIONS ------\n')
    print(">>>> EXACT MATCH PROPORTION <<<<")
    prop = exact(e2e=e2e)
    print(prop)
    print("\n>>>> BLEU SCORES <<<<")
    bs = bleu(e2e=e2e)
    print("** Golds against predictions **")
    print(bs[0].score)
    print("** Predictions against Golds **")
    print(bs[1].score)

if __name__ == "__main__":
    main()