import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from django.utils.module_loading import import_string  # NOQA
from .detect_varnames import get_setting_values


def iter_syspath(paths, settings_dir):
    assert settings_dir.is_dir()

    for pathname in paths:
        path = Path(pathname).absolute()
        if path.is_dir():  # todo: suport zipimport
            for child in path.iterdir():
                rel = child.relative_to(path)
                if rel.match(".*"):
                    print("skipping", child, file=sys.stderr)
                    continue

                if child.is_dir():
                    for name in child.glob("**/*.py"):
                        if not name.is_relative_to(settings_dir):
                            # ignore settings dir
                            yield name
                else:
                    if child.suffix == '.py':
                        yield child

def iter_conffiles(path):
    yield from path.glob("*.ini")
    yield from path.glob("*.yml")


def get_setting_names(settings_dir):
    results = {}
    for filename in Path(settings_dir).glob("**/*.py"):
        names, refs = get_setting_values(filename)
        results[str(filename)] = (names, refs)

    unused_names = set()
    # 他のsettingsモジュールで参照されている変数を除外
    for filename, (names, refs) in results.items():
        for k in results:
            if k != filename:
                unused_names.update(set(names) - set(refs))
    return unused_names


reobj = None
setting_names = None


def find_name(filename, settings_dir):
    global reobj, setting_names
    if setting_names is None:
        setting_names = get_setting_names(settings_dir)
        names = "|".join(sorted(setting_names, reverse=True))
        reobj = re.compile(rf"\b{names}\b")

    src = open(filename, errors="replace").read()
    matches = [s for s in reobj.findall(src)]
    return set(matches), filename, settings_dir


def main(settings_dir):
    settings_dir = os.path.abspath(settings_dir)
    seen = set()

    def done(fut):
        matches, _, _ = fut.result()
        seen.update(matches)

    with ProcessPoolExecutor() as e:
        paths = [p for p in sys.path if p not in ("", ".")]
        for n in iter_syspath(paths, Path(settings_dir)):
            fut = e.submit(find_name, n, settings_dir)
            fut.add_done_callback(done)
            print(f"Submitted {n}...", file=sys.stderr)

        for n in iter_conffiles(Path(".").absolute()):
            fut = e.submit(find_name, n, settings_dir)
            fut.add_done_callback(done)
            print(f"Submitted {n}...", file=sys.stderr)

    setting_names = get_setting_names(settings_dir)
    unused = sorted(setting_names - seen)
    if unused:
        print("未使用の可能性がある変数名:")
        for name in unused:
            print("- "+name)
        return True
    else:
        return False

if __name__ == "__main__":
    main(sys.argv[1])
