import nbformat
import random
import os
from .parseExamDirective import splitDirective, ExamDirectiveType
from pprint import pprint
import ast
import pathlib

# https://stackoverflow.com/questions/39379331/python-exec-a-code-block-and-eval-the-last-line
def exec_then_eval(code):
    block = ast.parse(code, mode='exec')

    # assumes last node is an expression
    last = ast.Expression(block.body.pop().value)

    _globals, _locals = {}, {}
    exec(compile(block, '<string>', mode='exec'), _globals, _locals)
    return eval(compile(last, '<string>', mode='eval'), _globals, _locals)

def handleNotebook(notebook_path, output_path):
    sourceNotebook = nbformat.read(notebook_path, as_version=4)
    examStructure = getExamStructure(sourceNotebook)
    examInfos = getExamInfos(sourceNotebook)
    for examInfo in examInfos:
        filename = examInfo['filename']
        cells,tests = generateNotebook(examStructure, examInfo)

        exams_dir = os.path.join(output_path, 'exams')
        tests_dir = os.path.join(output_path, 'tests')

        pathlib.Path(exams_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(tests_dir).mkdir(parents=True, exist_ok=True)
        nbformat.write(cellListToNotebook(cells), os.path.join(exams_dir, filename))
        nbformat.write(cellListToNotebook(tests), os.path.join(tests_dir, filename))

def cellListToNotebook(cells):
    notebook = nbformat.v4.new_notebook()
    cellObjects = []
    for cell in cells:
        if cell['cell_type'] == 'markdown':
            cellObjects.append(nbformat.v4.new_markdown_cell(cell['source']))
        elif cell['cell_type'] == 'code':
            cellObjects.append(nbformat.v4.new_code_cell(cell['source']))
    notebook['cells'] = cellObjects
    return notebook

def generateNotebook(examStructure, providedEnv={}):
    cells = []
    tests = []
    env = {
        'problem': 1,
        'points': 0
    }
    for key,val in providedEnv.items():
        env[key] = val

    for group in examStructure:
        problems = list(group['problems'].values())
        random.shuffle(problems)

        for problem in problems:
            directive = problem['directive']
            if directive and directive['type'] == ExamDirectiveType.PROBLEM:
                env['points'] = directive['points']

            selectedAlternative = random.choice(problem['alternatives'])

            for cell in selectedAlternative['cells']:
                cellCopy = cell.copy()
                for key in env:
                    cellCopy['source'] = cellCopy['source'].replace('@'+key+'', str(env[key]))
                cells.append(cellCopy)
            for test in selectedAlternative['tests']:
                testCopy = test.copy()
                tests.append(testCopy)

            if directive['type'] == ExamDirectiveType.PROBLEM:
                env['problem'] += 1

    return cells, tests

def getExamInfos(nb):
    for cell in nb.cells:
        cell_type = cell['cell_type']
        source = cell['source']
        if cell_type == 'code':
            directive, newSource = splitDirective(cell_type, source)
            if directive and directive['type'] == ExamDirectiveType.EXAMS:
                result = exec_then_eval(newSource)

                resultList = []

                for index, item in enumerate(result):
                    if type(item) == type({}):
                        if 'filename' not in item:
                            item['filename'] = '{}.ipynb'.format(index)
                        resultList.append(item)
                    else:
                        resultList.append({
                            'filename': str(item)
                        })
                return resultList

def getExamStructure(nb):
    cellsAndDirectives = []
    for cell in nb.cells:
        cell_type = cell['cell_type']
        source = cell['source']
        directive, newSource = splitDirective(cell_type, source)

        cellCopy = cell.copy()
        cellCopy['source'] = newSource
        cellsAndDirectives.append((directive, cellCopy))
    
    notebookGroups = []
    currentGroup = False
    currentProblem = False
    currentAlternative = False
    for directive,cell in cellsAndDirectives:
        if directive == False:
            if currentAlternative:
                currentAlternative['cells'].append(cell)
            else:
                notebookGroups.append({
                    'problems': {
                        None: {
                            'directive': directive,
                            'alternatives': [{
                                'cells': [cell],
                                'tests': []
                            }]
                        }
                    }
                })
        elif directive['type'] == ExamDirectiveType.ALWAYS_INCLUDE:
            currentAlternative = {
                'cells': [cell],
                'tests': []
            }
            currentProblem = {
                'directive': directive,
                'alternatives': [currentAlternative]
            }
            currentGroup = {
                'problems': { None: currentProblem }
            }
            notebookGroups.append(currentGroup)
        elif directive['type'] == ExamDirectiveType.PROBLEM:
            if currentProblem and currentProblem['directive']['type'] == directive['type'] and currentProblem['directive']['group'] == directive['group']:
                currentAlternative = {
                    'cells': [cell],
                    'tests': []
                }

                if directive['id'] in currentGroup['problems']:
                    currentGroup['problems'][directive['id']]['alternatives'].append(currentAlternative)
                else:
                    currentGroup['problems'][directive['id']] = {
                        'directive': directive,
                        'alternatives': [currentAlternative]
                    }
            else:
                currentAlternative = {
                    'cells': [cell],
                    'tests': []
                }
                currentProblem = {
                    'directive': directive,
                    'alternatives': [currentAlternative]
                }
                currentGroup = {
                    'problems': {directive['id']: currentProblem}
                }
                notebookGroups.append(currentGroup)
        elif directive['type'] == ExamDirectiveType.TEST:
            if directive['visible']:
                currentAlternative['cells'].append(cell)

            currentAlternative['tests'].append(cell)
        elif directive['type'] == ExamDirectiveType.EXAMS:
            continue
    return notebookGroups

def directiveMatches(d1, d2):
    if d1 == d2:
        return True
    elif (d1 == False and d2['type'] == ExamDirectiveType.ALWAYS_INCLUDE) or (d2 == False and d1['type'] == ExamDirectiveType.ALWAYS_INCLUDE):
        return True
    else:
        return d1 == d2