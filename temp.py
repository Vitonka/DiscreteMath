from pylatex import Document, Section, Subsection, Command, Enumerate
from pylatex.package import Package
from pylatex.utils import italic, NoEscape
import numpy as np
import os
import sys


TASK_DELIM = '---'
DEFAULT_TASK_TYPE = 1


def parse_task(path, all_variants=False):
    def parse_task_type(type_string):
        tokens = type_string.strip().split()
        for token in tokens:
            if token.isdigit():
                return int(token)
        return DEFAULT_TASK_TYPE

    # Task type 1: every task has its own description
    def parse_task_type_1(preparsed):
        if not all_variants:
            var = np.random.randint(len(preparsed))
            return preparsed[var], var + 1
        else:
            return preparsed, 0

    # Task type 2: all tasks have the same description, but different variants
    def parse_task_type_2(preparsed):
        if not all_variants:
            var = np.random.randint(len(preparsed) - 1)
            return preparsed[0] + '\n\n' + preparsed[var + 1], var + 1
        else:
            return [preparsed[0] + '\n\n' + p for p in preparsed[1:]], 0

    # TODO: Task type 2 extended: every task has its own description and variants
    # TODO: Tasks without types, uniform distribution

    with open(path) as f:
        parsed_file = [s.strip() for s in f.read().split(TASK_DELIM)]
        task_type = parse_task_type(parsed_file[0])
        task_data = parsed_file[1:]
        if task_type == 1:
            return parse_task_type_1(task_data)
        elif task_type == 2:
            return parse_task_type_2(task_data)
        else:
            print('Unsupported task type', file=sys.stderr)
            sys.exit()


def generate_lab_preambule(name):
    doc = Document(name, fontenc='T2A')
    doc.packages.append(Package('babel', 'russian'))
    doc.packages.append(Package('titling'))
    doc.packages.append(Package('nopageno'))
    doc.packages.append(Package('amsfonts'))
    doc.packages.append(Package('amssymb'))
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('geometry', 'left=2cm,right=2cm, top=2cm,bottom=2cm'))
    doc.packages.append(Package('circuitikz'))
    doc.preamble.append(Command('title', 'Лабораторная работа 1: Логика высказываний и её приложения'))
#    doc.preamble.append(Command('date', NoEscape('Дата сдачи: 23.12.1994')))
    doc.preamble.append(Command('date', ''))
    return doc


def generate_lab_content(doc, path, variant=0, all_variants=False):
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\vspace{-80pt}'))
    if variant > 0:
        doc.append(NoEscape(r'\begin{center}\Large{Вариант ' + str(variant) + r'}\end{center}'))
    cur_variant = []
    with doc.create(Enumerate()) as enum:
        for task_path in sorted(os.listdir(path)):
            tasks, var = parse_task(os.path.join(path, task_path), all_variants)
            if not all_variants:
                enum.add_item(NoEscape(tasks))
                cur_variant.append(var)
            else:
                enum_inside = Enumerate('\\arabic*.')
                for task in tasks:
                    enum_inside.add_item(NoEscape(task))
                enum.add_item(enum_inside)
    return cur_variant


def generate_labs(name='AllTasksVariants', count=1, path='Data/AllTasks/'):
    variants = []
    doc = generate_lab_preambule(name)
    for i in range(count):
        if i > 0:
            doc.append(Command('pagebreak'))
        variants.append(generate_lab_content(doc, path, i + 1))
    doc.generate_pdf(clean_tex=False)
    doc = generate_lab_preambule(name + '_variants')
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\vspace{-80pt}'))
    with doc.create(Enumerate()) as enum:
        for var in variants:
            var = zip(range(len(var)), var)
            enum.add_item(', '.join(map(lambda x: str(x[0] + 1) + '.' + str(x[1]), var)))
    doc.generate_pdf(clean_tex=False)


def generate_all_tasks(name='AllTasks', path='Data/AllTasks/'):
    doc = generate_lab_preambule(name)
    generate_lab_content(doc, path, all_variants=True)
    doc.generate_pdf(clean_tex=False)

if __name__ == '__main__':
    generate_labs('Lab1_Logic', 60, 'Data/Lab1_Logic')
    generate_all_tasks('Lab1_Logic_tasks', 'Data/Lab1_Logic')
