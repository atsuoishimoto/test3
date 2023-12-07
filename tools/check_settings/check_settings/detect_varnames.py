"""Detect names globally assgined and named used for referenfes"""

import ast
import sys
import os
import glob
import re


class WalkScope(ast.NodeVisitor):
    def __init__(self, add_globals, add_ref_names):
        super().__init__()
        self.add_globals = add_globals
        self.add_ref_names = add_ref_names

    def visit(self, node):
        match node:
            case ast.Global():
                self.add_globals(node.names)
                return

            case ast.Assign():
                # skip ast.Assign.targets
                if isinstance(node.value, ast.Name):
                    self.add_ref_names([node.value.id])
                else:
                    self.generic_visit(node.value)
                return

            case ast.Name():
                # The name was used in expr
                self.add_ref_names([node.id])
                return

            case ast.Attribute():
                # The name was used in expr
                self.add_ref_names([node.attr])
                return

        return self.generic_visit(node)


class WalkTarget(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.names = set()

    def visit(self, node):
        match node:
            case ast.Name():
                self.names.add(node.id)

            case ast.Attribute():
                self.names.add(node.attr)
                return self.generic_visit(node)


class SettingDetectVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.names = set()
        self.ref_names = set()

    def add_globals(self, names):
        names = list(names)
        self.names.update(names)

    def add_ref_names(self, names):
        self.ref_names.update(names)

    def _visit_refnodes(self, node):
        f = WalkScope(self.add_globals, self.add_ref_names)
        f.visit(node)

    def visit(self, node):
        match node:
            case ast.Import() | ast.ImportFrom():
                names = []
                for name in node.names:
                    modname = name.asname or name.name
                    if modname.isidentifier():
                        names.append(modname)

                self.add_globals(names)

            case ast.Assign():
                # Global assign
                for target in node.targets:
                    w = WalkTarget()
                    w.visit(target)
                    self.add_globals(w.names)

                if isinstance(node.value, ast.Name):
                    self.add_ref_names([node.value.id])
                else:
                    self.generic_visit(node.value)
                return

            case ast.Name():
                # The name was used in expr
                self.add_ref_names([node.id])
                return
            case ast.NamedExpr():
                w = WalkTarget()
                w.visit(node.target)
                self.add_globals(w.names)
                return

            case ast.FunctionDef() | ast.ClassDef():
                self.add_globals([node.name])
                self._visit_refnodes(node)
                return

        self.generic_visit(node)


def get_setting_values(filename):
    node = ast.parse(open(filename).read(), filename, "exec", type_comments=False)
    s = SettingDetectVisitor()
    s.visit(node)
    names = (name for name in s.names if re.match(r"^[^_][A-Z0-9_]*$", name))
    ref_names = (name for name in s.ref_names if re.match(r"^[^_][A-Z0-9_]*$", name))
    return sorted(names), sorted(ref_names)


if __name__ == "__main__":
    filename = sys.argv[1]
    if os.path.isdir(filename):
        filenames = list(glob.glob(os.path.join(filename, "*.py")))
    else:
        filenames = [filename]

    for filename in filenames:
        names, refs = get_setting_values(filename)
        print(filename, names, refs)
