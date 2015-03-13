#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

import sys
import argparse
import subprocess

import yaml
from jnpr.jsnap.hosts import Hosts
from jnpr.jsnap.snap import Parse
from jnpr.jsnap.check import Comparator
from jnpr.jsnap.testop import Operator
from jnpr.jsnap.notify import Notification


class Jsnap:

    # taking parameters from command line
    def __init__(self):
        global args
        self.parser = argparse.ArgumentParser()
        group = self.parser.add_mutually_exclusive_group()
        # for mutually exclusive gp, can not use both options
        group.add_argument(
            '--snap',
            action='store_true',
            help="take the snapshot")
        group.add_argument(
            '--check',
            action='store_true',
            help=" compare snapshots")
        group.add_argument(
            '--snapcheck',
            action='store_true',
            help='check current snapshot')
        group.add_argument(
            "--init",
            action="store_true",
            help="init file",
        )
        self.parser.add_argument(
            "out_file1",
            nargs='?',
            help="output file1")       # make it optional
        self.parser.add_argument(
            "out_file2",
            nargs='?',
            help="output file2",
            type=str)       # make it optional
        self.parser.add_argument(
            "-f", "--file",
            help="config file to take snapshot",
            type=str)
        self.parser.add_argument("-t", "--hostname", help="hostname", type=str)
        self.parser.add_argument(
            "-p",
            "--passwd",
            help="password to login",
            type=str)
        self.parser.add_argument(
            "-l",
            "--login",
            help="username to login",
            type=str)
        self.args = self.parser.parse_args()
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(1)

    # call hosts class, connect hosts and get host list
    def get_hosts(self):
        # os.chdir('..')
        output_file = self.args.out_file1
        #path = os.getcwd()
        #conf_file = path + '/' + 'ConfigFiles' + '/' + config_file
        conf_file = self.args.file
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        h = Hosts()
        self.devices = h.login(self.args, main_file, output_file)
        self.host_list = h.hostname_list
        return main_file, self.host_list

    # call to generate snap files
    def generate_rpc_reply(self, main_file):
        test_files = []
        for mfile in main_file['tests']:
            test_file = open(mfile, 'r')
            test_files.append(yaml.load(test_file))
        g = Parse()
        for tests in test_files:
            g.generate_reply(tests, self.devices)

    # called by check and snapcheck argument, to compare snap files
    def compare_tests(self, main_file):
        comp = Comparator()
        chk = d.args.check
        if (chk):
            comp.generate_test_files(
                main_file,
                self.host_list,
                chk,
                self.args.out_file1,
                self.args.out_file2)
        else:
            comp.generate_test_files(
                main_file,
                self.host_list,
                chk,
                self.args.out_file1)

    # generate init folder
    def generate_init(self):
        p = subprocess.Popen(["mkdir", "snapshots"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        p = subprocess.Popen(["cp",
                              "-r",
                              "/Library/Python/2.7/site-packages/jnpr/jsnap/configs",
                              "."],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        p = subprocess.Popen(["cp",
                              "/Library/Python/2.7/site-packages/jnpr/jsnap/configs/main.yml",
                              "."],
                             stdout=subprocess.PIPE)


def main():
    d = Jsnap()

    # make init folder
    if d.args.init is True:
        d.generate_init()

    # check for option: snap, check, snapcheck
    elif(d.args.file):
        mainfile, hostlists = d.get_hosts()
        if d.args.snap is True:
            d.generate_rpc_reply(mainfile)
        if d.args.check is True or d.args.snapcheck is True:
            d.compare_tests(mainfile)
            obj = Operator()
            obj.final_result()
            if mainfile.get('mail'):
                send_mail = Notification()
                send_mail.notify(mainfile['mail'], hostlists)

if __name__ == '__main__':
    main()
