"""
INSPECTION DATA - Evaluation du moteur.
Compare les anomalies detectees a la verite terrain injectee.
"""

def _metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    rappel = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * rappel / (precision + rappel) if (precision + rappel) else 0.0
    return {"precision": round(precision, 3), "rappel": round(rappel, 3),
            "f1": round(f1, 3), "tp": tp, "fp": fp, "fn": fn}


def evaluate(results, ground_truth_df):
    gt_by = ground_truth_df.groupby("control_id")["id"].apply(set).to_dict()
    par_controle = {}
    TP = FP = FN = 0
    for c in results:
        detected = set(c["ids"])
        gt = gt_by.get(c["id"], set())
        tp, fp, fn = len(detected & gt), len(detected - gt), len(gt - detected)
        TP += tp; FP += fp; FN += fn
        par_controle[c["id"]] = _metrics(tp, fp, fn)
    return {"global": _metrics(TP, FP, FN), "par_controle": par_controle}
