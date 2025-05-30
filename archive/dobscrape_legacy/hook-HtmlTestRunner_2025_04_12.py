# Copilot: Summarize what this file does and why it may have been replaced or archived.

# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# Hook for HtmlTestRunner: https://pypi.org/project/html-testRunner//1.2.1

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('HtmlTestRunner')
