import git
import paramiko
import argparse
import time
import os
from datetime import datetime
from scp import SCPClient
from shutil import copyfile

parser = argparse.ArgumentParser(description='Exit Logic')
parser.add_argument('-sfp', '--sfp', help='Source file Path', required=True)
parser.add_argument('-repo_loc', '--repo_loc', help='Repo Loc', required=True)

args = parser.parse_args()

repo_loc = args.repo_loc
src_file_path = args.sfp

repo = git.Repo(repo_loc)
diff = repo.git.diff(name_only=True)
date_str = datetime.now().strftime("%Y%m%d")

if len(diff) > 0:
    print('list of modified list\n', diff)
    raise Exception("First Commit Files")


def get_remote_file_name():
    # branch_name = repo.active_branch.name
    repo_name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
    commit_name = str(time.time())
    file_name = repo_name + '_' + commit_name + '_' + date_str
    return file_name



ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def transfer_file():
    ssh.connect(ip, username=user_name, allow_agent=True)
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(src_file_path, remote_file_path)


def transfer_local():
    #os.system("cp -r {} {}".format(src_file_path, repo_loc ))
    lrepo = git.Repo(repo_loc)
    lrepo.git.add(A=True)
    lrepo.git.commit(m=get_remote_file_name())


#transfer_file()
transfer_local()
