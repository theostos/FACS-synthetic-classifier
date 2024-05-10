import json

upper = json.load(open('upper.json', 'r'))
lower = json.load(open('lower.json', 'r'))

upper_l = {}
upper_r = {}
upper_c = {}

lower_l = {}
lower_r = {}
lower_c = {}

for param_u in upper:
    if '_R_' in param_u:
        upper_r[param_u] = upper[param_u]
    elif '_L_' in param_u:
        upper_l[param_u] = upper[param_u]
    elif '_C_' in param_u:
        upper_c[param_u] = upper[param_u]
    else:
        raise Exception(f"Sorry, unknown location for {param_u} in upper parameters")

for param_u in lower:
    if '_R_' in param_u:
        lower_r[param_u] = lower[param_u]
    elif '_L_' in param_u:
        lower_l[param_u] = lower[param_u]
    elif '_C_' in param_u:
        lower_c[param_u] = lower[param_u]
    else:
        raise Exception(f"Sorry, unknown location for {param_u} in lower parameters")

file_upper_l = open('upper_l.json', 'w')
file_upper_r = open('upper_r.json', 'w')
file_upper_c = open('upper_c.json', 'w')

file_lower_l = open('lower_l.json', 'w')
file_lower_r = open('lower_r.json', 'w')
file_lower_c = open('lower_c.json', 'w')

json.dump(upper_l, file_upper_l, indent=4)
json.dump(upper_r, file_upper_r, indent=4)
json.dump(upper_c, file_upper_c, indent=4)

json.dump(lower_l, file_lower_l, indent=4)
json.dump(lower_r, file_lower_r, indent=4)
json.dump(lower_c, file_lower_c, indent=4)
