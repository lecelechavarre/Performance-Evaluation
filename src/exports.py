import pandas as pd

def export_evaluations_to_excel(evaluations, criteria, out_path):
    rows = []
    for ev in evaluations:
        row = {
            'eval_id': ev['id'],
            'employee_id': ev['employee_id'],
            'evaluator_id': ev['evaluator_id'],
            'date': ev['date'],
            'comments': ev.get('comments','')
        }
        for cid, score in ev['scores'].items():
            row[cid] = score
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_excel(out_path, index=False)
