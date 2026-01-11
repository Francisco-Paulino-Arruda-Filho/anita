import anita.anita_en_fo
import argparse
import traceback
from anita.i18n import t

parser = argparse.ArgumentParser(description='Analytic Tableau Proof Assistant (ANITA).')
parser.add_argument("-i", type=str,help="Input file with the proof in ANITA.")
parser.add_argument("-o", type=str,help="Output file of result of the checking of the proof in ANITA.")
args = parser.parse_args()
fileName = 'example_anita_en.txt'
fileSave = 'result_anita_en.txt'
if args.i is not None: fileName = args.i
if args.o is not None: fileSave = args.o
try:
    f = open(fileName, 'r')
    input_proof = f.read()
    result = anita.anita_en_fo.ParserAnita.getProof(input_proof)
    with open(fileSave, "w", encoding='utf8') as fs:
        if(result.errors==[]):
            if(result.is_closed):
                fs.write(t("FILE_OUTPUT_PROOF_VALID", "en"))
                fs.write(result.theorem) 
                fs.write("\n;"+str(result.latex))
                fs.write(";"+t("FILE_OUTPUT_THEOREM_PROOF_VALID", "en").format(result.latex_theorem))
                fs.write("\n"+str(result.colored_latex))
            else:
                if result.saturared_branches != []:
                    fs.write(t("FILE_OUTPUT_THEOREM_NOT_VALID", "en"))
                    fs.write(result.theorem) 
                    fs.write("\n"+t("FILE_OUTPUT_COUNTERMODELS", "en"))
                    for s_v in result.counter_examples:
                        fs.write('\n  '+s_v)
                    fs.write("\n;"+str(result.latex))
                    fs.write(";"+t("FILE_OUTPUT_LATEX_THEOREM_NOT_VALID", "en").format(result.latex_theorem))
                    fs.write("\n"+t("FILE_OUTPUT_COUNTERMODELS", "en"))
                    fs.write("\n\\begin{itemize}")
                    for s_v in result.counter_examples:
                        fs.write('\n  \\item $'+s_v+'$')
                    fs.write("\n\\end{itemize}")
                    fs.write("\n"+str(result.colored_latex))
                else: 
                    fs.write(t("FILE_OUTPUT_PROOF_NOT_COMPLETE", "en"))
                    fs.write(result.theorem) 
                    fs.write("\n"+t("FILE_OUTPUT_BRANCHES_NOT_SATURATED", "en"))
                    for rules in result.open_branches:
                        fs.write("\n"+t("FILE_OUTPUT_BRANCH", "en"))
                        fs.write('\n  '.join([r.toString() for r in reversed(rules)]))
                    fs.write("\n;"+str(result.latex))
                    fs.write(";"+t("FILE_OUTPUT_LATEX_PROOF_NOT_COMPLETE", "en").format(result.latex_theorem))
                    fs.write("\n"+str(result.colored_latex))

        else:
            fs.write(t("FILE_OUTPUT_ERRORS_FOUND", "en"))
            for error in result.errors:
                fs.write(str(error))
    fs.close()
except ValueError:
    s = traceback.format_exc()
    result = (s.split("@@"))[-1]
    with open(fileSave, "w", encoding='utf8') as fs:
        fs.write(t("FILE_OUTPUT_ERRORS_FOUND", "en"))
        fs.write(result)
    print (f'{result}')
else:
    pass
