#!/usr/bin/env python3
"""Launch the zero-copy demo in a subprocess with a timeout and cleanup.

Usage:
    python scripts/run_zero_copy_safe.py [--timeout SECONDS]

This will start `test-skia-pyglet-zero-copy.py` in a child process and wait up to
`timeout` seconds. If the child process is still running after the timeout it
will be terminated to avoid unkillable/hung processes.
"""
import argparse
import subprocess
import sys
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument('--timeout', type=float, default=10.0, help='seconds to wait before killing the demo')
parser.add_argument('--python', type=str, default=None, help='Python interpreter to run the demo with (defaults to launcher interpreter)')
args = parser.parse_args()

script = os.path.join(os.path.dirname(__file__), '..', 'test-skia-pyglet-zero-copy.py')
script = os.path.abspath(script)
if not os.path.exists(script):
    print('Zero-copy script not found:', script)
    sys.exit(2)

python_bin = args.python if args.python else sys.executable
cmd = [python_bin, '-u', script, '--zero-copy']
print('Starting zero-copy demo subprocess:', cmd)
env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'
# start in a new process group so we can kill children that spawn their own processes
start_new_session = True if hasattr(os, 'setsid') else False
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env, start_new_session=start_new_session)
start = time.time()
try:
    while True:
        if proc.poll() is not None:
            print('Child exited with', proc.returncode)
            # print remaining output
            out = proc.stdout.read() if proc.stdout is not None else None
            if out:
                print(out)
            break
        if (time.time() - start) > args.timeout:
            print(f'Timeout reached ({args.timeout}s), terminating child (pid={proc.pid})')
            try:
                # attempt to terminate the whole session / process group
                if start_new_session:
                    os.killpg(os.getpgid(proc.pid), 15)  # SIGTERM
                else:
                    proc.terminate()
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            # give a short grace then force kill
            time.sleep(0.5)
            if proc.poll() is None:
                try:
                    if start_new_session:
                        os.killpg(os.getpgid(proc.pid), 9)  # SIGKILL
                    else:
                        proc.kill()
                except Exception:
                    pass
            try:
                out = proc.stdout.read() if proc.stdout is not None else None
                if out:
                    print(out)
            except Exception:
                pass
            break
        # read any available output without blocking
        try:
            if proc.stdout is not None:
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
        except Exception:
            pass
        time.sleep(0.1)
except KeyboardInterrupt:
    print('Interrupted by user, terminating child')
    try:
        proc.kill()
    except Exception:
        pass
    sys.exit(1)

print('Launcher done')
