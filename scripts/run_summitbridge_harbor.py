"""Run SummitBridge references or one assignment-endpoint model rollout through Harbor."""
import argparse
import datetime
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / 'environments/summitbridge-email-supervisor'
HARBOR = shutil.which('harbor') or str(Path.home()/'.local/share/uv/tools/harbor/bin/harbor')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['starter','safe','unsafe','model'],required=True)
    args=parser.parse_args()
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    env=os.environ.copy()
    task=TASK
    # Harbor's oracle always runs solution/solve.sh. Give the unsafe reference
    # its own complete task copy so the original safe reference is unchanged.
    if args.mode=='unsafe':
        task=ROOT/'results/summitbridge-email-supervisor/reference-tasks'/('unsafe-'+stamp)
        shutil.copytree(TASK,task,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
        shutil.rmtree(task/'solution')
        shutil.copytree(TASK/'unsafe_reference',task/'solution')
    command=[HARBOR,'run','-p',str(task),'-a','nop' if args.mode=='starter' else 'oracle',
             '-k','1','-o',str(ROOT/'results/summitbridge-email-supervisor/harbor'),
             '--job-name',args.mode+'-'+stamp]
    if args.mode=='model':
        settings=json.loads((ROOT/'private/solumn_endpoint.json').read_text())
        env['OPENAI_API_KEY']=settings['api_key']
        env['OPENAI_BASE_URL']=settings['base_url']
        command[command.index('-a')+1]='terminus-2'
        command += ['-m','openai/gpt-6.1-sol','--ak','reasoning_effort=high',
                    '--ak','api_base='+settings['base_url'],
                    '--ak','llm_kwargs={"timeout":900,"stream":false}',
                    '--ak','max_turns=20']
    print('Starting Harbor mode:',args.mode,flush=True)
    # Credentials are only in the parent environment, never command arguments.
    raise SystemExit(subprocess.call(command,env=env,cwd=ROOT))


if __name__=='__main__':
    main()
