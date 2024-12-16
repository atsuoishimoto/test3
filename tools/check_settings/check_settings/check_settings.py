import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .detect_varnames import get_setting_values


def iter_syspath(paths, settings_dir):
    assert settings_dir.is_dir()
    seen = set()
    for pathname in paths:
        path = Path(pathname).absolute()
        if path in seen:
            continue
        seen.add(path)
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
                    if child.suffix == ".py":
                        yield child


def iter_conffiles(path):
    yield from path.glob("*.ini")
    yield from path.glob("*.yml")


def get_setting_names(settings_dir):
    results = {}
    unused_names = set()

    for filename in Path(settings_dir).glob("**/*.py"):
        names, refs = get_setting_values(filename)
        results[str(filename)] = (names, refs)
        unused_names.update(set(names))

    # 他のsettingsモジュールで参照されている変数を除外
    for filename, (names, refs) in results.items():
        for k in results:
            other_names, other_refs = results[k]
            unused_names -= set(other_refs)

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
    setting_names = get_setting_names(settings_dir)

    if not setting_names:
        return False

    def done(fut):
        matches, _, _ = fut.result()
        seen.update(matches)

    numfiles = 0
    with ProcessPoolExecutor() as e:
        paths = [p for p in sys.path if p not in ("", ".")]
        for n in iter_syspath(paths, Path(settings_dir)):
            fut = e.submit(find_name, n, settings_dir)
            fut.add_done_callback(done)
            numfiles += 1

        for n in iter_conffiles(Path(".").absolute()):
            fut = e.submit(find_name, n, settings_dir)
            fut.add_done_callback(done)
            numfiles += 1

    print(f"{numfiles} files have been checked", file=sys.stderr)

    unused = sorted(setting_names - seen)
    if unused:
        print("未使用の可能性がある変数名:")
        for name in unused:
            print("- " + name)
        return True
    else:
        return False


if __name__ == "__main__":
    main(sys.argv[1])
