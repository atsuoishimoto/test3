"""
settingsで設定されているが、プロジェクト、またはDjangoなどの関連ライブラリで参照されていない変数名を検出します。
https://github.com/Nikkei/api-gateway/issues/5316

使い方:
$ python -m check_settings path-for-setting-files
"""

import sys

from . import check_settings

ret = check_settings.main(sys.argv[1])
sys.exit(ret)
