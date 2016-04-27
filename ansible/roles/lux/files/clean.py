import os
import shutil


def clean():
    skip = set((os.path.basename(os.path.realpath('latest')),
                os.path.basename(os.path.realpath('running')),
                os.path.basename(os.path.realpath('rollback'))))
    count = 0
    for name in os.listdir('.'):
        if (not os.path.isdir(name) or
                name in skip or
                not name.startswith('20')):
            continue
        shutil.rmtree(name)
        count += 1

    print('removed %d directories' % count)


if __name__ == '__main__':
    clean()
