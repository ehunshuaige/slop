#!/usr/bin/env python3
"""Drop the parts of an iOS root that the lock screen and SpringBoard never load.

usage: root-trim.py MOUNT_POINT

The image has to fit DarwinBoot's RAM window when there is no UFS root driver, so
this removes Siri and language data, preinstalled media, apps that only make sense
with accounts, and every localisation except English and Simplified Chinese.
Requires root to remove files owned by other users.
"""
import os
import shutil
import sys

DROPPABLE = [
    'System/Library/Assistant',
    'System/Library/PreinstalledAssetsV2',
    'System/Library/Health',
    'System/Library/NanoTimeKit',
    'System/Library/ScreenReader',
    'System/Library/Carrier Bundles',
    'System/Library/LinguisticData',
    'System/Library/Fonts/LanguageSupport',
    'System/Library/Fonts/Supplemental',
    'System/Library/PrivateFrameworks/HealthUI.framework',
    'System/Library/PrivateFrameworks/VoiceTrigger.framework',
    'System/Library/PrivateFrameworks/SiriTTS.framework',
    'Applications/Health.app',
    'Applications/Tips.app',
    'Applications/Books.app',
    'Applications/Stocks.app',
    'Applications/News.app',
    'Applications/Maps.app',
    'Applications/Fitness.app',
    'Applications/Home.app',
    'Applications/Shortcuts.app',
    'Applications/Journal.app',
    'Applications/Translate.app',
    'Applications/Podcasts.app',
    'Applications/Music.app',
    'Applications/TV.app',
    'Applications/Videos.app',
    'Applications/Measure.app',
    'Applications/VoiceMemos.app',
]
KEEP_LANGS = {'en.lproj', 'zh-Hans.lproj', 'Base.lproj', 'English.lproj', 'en_US.lproj'}


def size_of(path):
    total = 0
    for base, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(base, name))
            except OSError:
                pass
    return total


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    if not os.path.isdir(root):
        sys.exit(f'{root}: not a directory')
    print(f'{root}: before {size_of(root) / 2**20:.0f} MiB')

    removed = 0
    for rel in DROPPABLE:
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            continue
        if os.path.islink(full):
            os.unlink(full)
        else:
            shutil.rmtree(full, ignore_errors=True)
        removed += 1
    print(f'dropped {removed} app/resource groups')

    count = 0
    for base, dirs, _files in os.walk(root):
        for name in list(dirs):
            if name.endswith('.lproj') and name not in KEEP_LANGS:
                shutil.rmtree(os.path.join(base, name), ignore_errors=True)
                dirs.remove(name)
                count += 1
    print(f'dropped {count} non-primary localisation directories')
    print(f'{root}: after  {size_of(root) / 2**20:.0f} MiB')


if __name__ == '__main__':
    main()
