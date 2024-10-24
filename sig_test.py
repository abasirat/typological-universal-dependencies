import sys
import pyconll
import random
from statsmodels.stats.contingency_tables import mcnemar

ud_pred, ud_gold, croft_pred, croft_gold = sys.argv[1:]


def contingency_table(ud_gold, ud_pred, croft_gold, croft_pred):
    assert len(ud_gold) == len(ud_pred)
    assert len(croft_gold) == len(ud_pred)
    assert len(croft_pred) == len(ud_pred)

    ud_true_croft_true = 0
    ud_true_croft_false = 0
    ud_false_croft_true = 0
    ud_false_croft_false = 0

    for sid in range(len(ud_gold)):
        ud_gold_snt = ud_gold[sid]
        ud_pred_snt = ud_pred[sid]

        croft_gold_snt = croft_gold[sid]
        croft_pred_snt = croft_pred[sid]

        assert len(ud_pred_snt) == len(ud_gold_snt)
        assert len(croft_pred_snt) == len(ud_gold_snt)
        assert len(croft_pred_snt) == len(ud_gold_snt)


        for tid in range(len(ud_gold_snt)):
            u = (ud_gold_snt[tid].deprel == ud_pred_snt[tid].deprel and ud_gold_snt[tid].head == ud_pred_snt[tid].head)
            c = (croft_gold_snt[tid].deprel == croft_pred_snt[tid].deprel and croft_gold_snt[tid].head == croft_pred_snt[tid].head)

            ud_true_croft_true += int(u == True and c == True)
            ud_true_croft_false += int(u == True and  c == False)
            ud_false_croft_true += int(u == False and c == True)
            ud_false_croft_false += int(u == False and c == False)
    return [[ud_true_croft_true, ud_true_croft_false],[ud_false_croft_true, ud_false_croft_false]]


if __name__ == '__main__':
    ud_pred = pyconll.load_from_file(ud_pred)
    ud_gold = pyconll.load_from_file(ud_gold)

    croft_pred = pyconll.load_from_file(croft_pred)
    croft_gold = pyconll.load_from_file(croft_gold)

    ctable = contingency_table(ud_gold, ud_pred, croft_gold, croft_pred)
    print(mcnemar(ctable, exact=True, correction=False))
