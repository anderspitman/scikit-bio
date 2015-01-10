#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
import argparse
import subprocess
import yaml
from urllib import urlretrieve

TEST_DIRNAME = ".test_sandbox"
CONDA_DIRNAME = "conda"

TEST_DIR = os.path.join(os.getcwd(), TEST_DIRNAME)
CONDA_DIR = os.path.join(TEST_DIR, CONDA_DIRNAME)

class Environment(object):
    def __init__(self, env_vars):
        self._vars = env_vars
        self._prev_var_vals = {}

    def activate(self):
        for var_name in self._vars:
            self._prev_var_vals[var_name] = os.environ.get(var_name)
            os.environ[var_name] = self._vars[var_name]

    def deactivate(self):
        for var_name in self._prev_var_vals:
            if self._prev_var_vals[var_name] is not None:
                os.environ[var_name] = self._prev_var_vals[var_name]
            else:
                del os.environ[var_name]

class Environment_Manager(object):
    def __init__(self):
        with open(".travis.yml", "r") as stream:
            travis_config = yaml.load(stream)
        self._envs = []
        for line in travis_config["env"]:
            env_vars = {}
            for var in line.split():
                var_name, var_val = self._read_var(var)
                env_vars[var_name] = var_val
            #print(env_vars)
            env = Environment(env_vars)
            self._envs.append(env)

    def _read_var(self, line):
        eq_idx = line.index('=')
        var = line[:eq_idx]
        val = line[eq_idx+1:].replace('\'', '')
        return var, val

    def get_environments(self):
        return self._envs
        

def setup_conda():
    conda_filename = "Miniconda3-3.7.3-Linux-x86_64.sh"
    conda_path = os.path.join(TEST_DIR, conda_filename)
    #print(conda_path)
    if not os.path.exists(conda_path):
        os.mkdir(TEST_DIR)
        #conda_url = "http://repo.continuum.io/miniconda/"+conda_filename
        conda_url = "http://anderspitman.com"
        urlretrieve(conda_url, conda_path)

def run_command(command_str):
    command = command_str.split()
    #print(command)
    subprocess.call(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple task runner.')
    parser.add_argument('task_name')
    args = parser.parse_args()

    is_travis = os.environ.get('TRAVIS') == 'TRUE'

    # If running under travis, it will take care of setting environment
    # variables. Otherwise, we need to parse .travis.yml and run everythin
    # within each environment
    if is_travis:
        setup_conda()
    else:
        envs = Environment_Manager().get_environments()
        for env in envs:
            env.activate()
            run_command("bash test.sh")
            env.deactivate()

