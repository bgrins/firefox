import json
import os
from pathlib import Path
import shutil
import tempfile

import run
import launch

policy=json.loads((run.HERE/'POLICY.json').read_text())
run.authenticate(policy)
tmp=Path(tempfile.mkdtemp(prefix='css-chrome-import-',dir='/private/tmp'))
try:
    output=tmp/'output';output.mkdir()
    work=tmp/'work';work.mkdir()
    args=run.prepare(policy,output,work)
    runner, commandline, chrome=launch.bootstrap(run.ROOT)
    parser=commandline.create_parser(['chrome'])
    options=vars(parser.parse_args(args))
    commandline.check_args(options)
    chrome.check_args(**options)
    assert options['product'].name=='chrome' and options['enable_experimental'] is False
    assert options['manifest_update'] is False and options['manifest_download'] is False
    assert options['ssl_type']=='none' and options['processes']==1 and options['headless'] is True
    assert options['binary_args']==['--user-data-dir='+str(work/'profile')]
    assert options['include']==[policy['page']]
    from wptrunner import testloader
    print(json.dumps({'import_and_argument_admission':True,'product':options['product'].name,
      'browser_version':options['browser_version'],'ssl_type':options['ssl_type'],
      'experimental':options['enable_experimental'],'browser_executed':False,'dependencies_installed':False}))
finally:
    shutil.rmtree(tmp)
