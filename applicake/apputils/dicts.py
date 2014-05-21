#http://stackoverflow.com/a/12735459
def merge(dict_1, dict_2, priority='left'):
    d1 = dict_1.copy()
    d2 = dict_2.copy()
    if priority == 'left':
        return dict(d2, **d1)
    elif priority == 'right':
        return dict(d1, **d2)
    elif priority == 'append':
        for key in d2:
            if not key in d1:
                d1[key] = d2[key]
            else:
                if not isinstance(d1[key], list):
                    d1[key] = [d1[key]]
                if not isinstance(d2[key], list):
                    d2[key] = [d2[key]]
                d1[key].extend(d2[key])
        return d1


def unify(seq, unlist_single=True):
    if not isinstance(seq, list):
        return seq

    res = []
    for i in seq:
        if not i in res:
            res.append(i)
    if unlist_single and len(res) == 1:
        return res[0]
    else:
        return res
