import os
from enum import Enum

directivePrefix = '..'

class ExamDirectiveType(Enum):
    ALWAYS_INCLUDE = '*'
    PROBLEM = 'problem'
    TEST = 'test'
    EXAMS = 'exams'
    SOLUTION = 'solution'

def splitDirective(cellType, source):
    if cellType == 'markdown':
        if source[0:len(directivePrefix)] == directivePrefix:
            lines = source.splitlines()
            directive = parseDirective(lines[0].strip())

            newSource = os.linesep.join(lines[1:]).lstrip()
            return (directive, newSource)
    elif cellType == 'code':
        if source[0:len(directivePrefix)+1] == '#'+directivePrefix:
            lines = source.splitlines()
            directive = parseDirective(lines[0][1:].strip())

            newSource = os.linesep.join(lines[1:]).lstrip()
            return (directive, newSource)


    return (False, source)

def parseDirective(fullDirective):
    directive = fullDirective[len(directivePrefix):]
    splitDirective = directive.split()

    if splitDirective[0] == '*':
        return {
            'type': ExamDirectiveType.ALWAYS_INCLUDE
        }
    elif splitDirective[0].lower() == 'test':
        visible = True
        if len(splitDirective) >= 2:
            visible = splitDirective[1].lower() != 'hidden'

        return {
            'type': ExamDirectiveType.TEST,
            'visible': visible
        }
    elif splitDirective[0].lower() == 'problem':
        directiveType = ExamDirectiveType.PROBLEM

        [problemGroup, problemID] = splitDirective[1].split('.')
        if len(splitDirective) >= 3:
            points = int(splitDirective[2])
        else:
            points = False
        return {
            'type': ExamDirectiveType.PROBLEM,
            'group': problemGroup,
            'id': problemID,
            'points': points
        }
    elif splitDirective[0].lower() == 'exams':
        return {
            'type': ExamDirectiveType.EXAMS
        }
    elif splitDirective[0].lower() == 'solution':
        return {
            'type': ExamDirectiveType.SOLUTION
        }
    else:
        raise ValueError('Unknown directive "{}"'.format(splitDirective[0]))