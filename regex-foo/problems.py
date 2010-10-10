import re

pm_fieldnames = 'description hint solution_pattern user_pattern flags test'.split()

class ProblemException(Exception):
    pass


class PMProblem(object):
    fieldnames = pm_fieldnames
    user_pattern = ''
    def __init__(self, problem_text):
        self.flags = [] # optional field
        # hack for the last line
        problem_text = problem_text.rstrip('\n')
        field = None
        for l in problem_text.split('\n'):
            if not l:
                raise ProblemException('Invalid input (empty line): state: %s' % self.__dict__, problem_text)
            if l[0] == ' ':
                fval = getattr(self, field)
                fval.append(l[1:])
                continue
            l = l.strip()
            if l[:-1] in self.fieldnames and l[-1] == ':':
                field = l[:-1]
                setattr(self, field, [])
                continue
            raise ProblemException("Invalid problem input: line='%s'" % l, problem_text)
        for f in self.fieldnames:
            if not hasattr(self, f):
                raise ProblemException("Invalid problem input: missing field: %s" % f, problem_text)
            fval = getattr(self, f)
            if fval is not None:
                if f == 'flags':
                    new_fval = 0
                    for name in fval:
                        name=name.strip()
                        new_fval |= getattr(re, name)
                else:
                    new_fval = '\n'.join(fval)
                setattr(self, f, new_fval)

sr_fieldnames = pm_fieldnames[:]
sr_fieldnames.append('solution_replacement')

class SRProblem(PMProblem):
    fieldnames = sr_fieldnames
    user_replace = ''

def LoadProblems(filename, ProblemObj):
    f = open(filename)
    data = f.read()
    f.close()
    problems = []
    for problem_text in data.split('\n\n'):
        try:
            problem = ProblemObj(problem_text)
        except:
            print data
            raise
        #print "adding %s" % problem.__dict__
        problems.append(problem)
    return problems

def LoadPMProblems(filename=None):
    if filename == None:
        filename = 'pm.dat'
    return LoadProblems(filename, PMProblem)

def LoadSRProblems(filename=None):
    if filename == None:
        filename = 'sr.dat'
    return LoadProblems(filename, SRProblem)

