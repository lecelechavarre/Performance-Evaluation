import pandas as pd

def export_evaluations_to_excel(evaluations, criteria_map, out_path):
    rows = []
    for ev in evaluations:
        row = {'eval_id': ev['id'], 'employee_id': ev['employee_id'], 'evaluator_id': ev['evaluator_id'], 'date': ev['date'], 'comments': ev.get('comments','')}
        for cid, score in ev.get('scores', {}).items():
            label = criteria_map.get(cid, cid)
            row[label] = score
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_excel(out_path, index=False)
