import sys
import os
sys.path.append('../../../scripts')
import input as inp
# import output as oup
import dakota.interfacing as di
import subprocess
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Dymond
# -------------------------------

# Edit Dymond6 input file
cyclus_template = '../../../cyclus-files/oat/cooling-time/cooling-time.xml.in'
scenario_name = 'CT' + str(int(params['ct']))
variable_dict = {'handle': scenario_name, 'cooling_time': int((params['ct']*12))}
output_xml = '../../../cyclus-files/oat/cooling-time/cooling-time.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Run Cyclus with edited input file
output_sqlite = '../../../cyclus-files/oat/cooling-time/cooling-time.sqlite'
os.system('cyclus -i ' + output_xml + ' -o ' + output_sqlite)
# ----------------------------
# Return the results to Dakota
# ----------------------------

for i, r in enumerate(results.responses()):
    if r.asv.function:
        r.function = 1
        print('OUT', i, r.function)

results.write()
